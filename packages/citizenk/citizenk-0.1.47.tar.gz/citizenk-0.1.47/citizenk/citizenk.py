import asyncio
import json
import logging
import os
import signal
import socket
import threading
import time
from datetime import datetime
from enum import Enum
from functools import wraps
from inspect import signature
from typing import Callable, List, Optional, Union

import httpx
from confluent_kafka import KafkaException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .agent import Agent, WebSocketAgent
from .kafka_adapter import KafkaAdapter, KafkaConfig, KafkaRole
from .topic import Topic, TopicDir
from .utils import CitizenKError

logger = logging.getLogger(__name__)


class AppType(Enum):
    SOURCE = 1
    SINK = 2
    TRANSFORM = 3


class CitizenK(FastAPI):
    def __init__(
        self,
        kafka_config: KafkaConfig,
        app_name: str,
        app_type: AppType = AppType.SOURCE,
        consumer_group_init_offset: str = "latest",
        schema_registry_url: Optional[str] = None,
        auto_generate_apis: bool = True,
        max_processing_cycle_ms: int = 5 * 1000,
        api_router_prefix: str = "",
        api_port: Optional[int] = None,
        agents_in_thread: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.app_name = app_name
        self.app_type = app_type
        self.kafka_config = kafka_config
        self.consumer_group_init_offset = consumer_group_init_offset
        self.schema_registry_url = schema_registry_url
        self.auto_generate_apis = auto_generate_apis
        self.max_processing_cycle_ms = max_processing_cycle_ms
        self.api_router_prefix = api_router_prefix
        self.api_port = api_port
        self.producer = None
        self.consumer = None
        self._started = datetime.utcnow()

        self.total_batch_size = 0
        self.consumer_topics = set()
        self.topics = {}
        self.agents = {}
        self.websocket_agents = {}
        self.agents_in_thread = agents_in_thread
        self.background_loop = None
        self.background_thread = None
        self.main_consumer_loop_task = None
        self.monitor_loop_task = None

        self.add_event_handler("startup", self.startup)
        self.add_event_handler("shutdown", self.shutdown)
        if auto_generate_apis:
            self._generate_apis()

    def _generate_apis(self):
        @self.get(
            f"{self.api_router_prefix}/stats/producer", response_class=JSONResponse
        )
        def get_producer_stats():
            """Get the producer stats"""
            if self.producer is not None:
                return self.producer.last_stats
            return {}

        @self.get(
            f"{self.api_router_prefix}/stats/consumer", response_class=JSONResponse
        )
        def get_consumer_stats():
            """Get the producer stats"""
            if self.consumer is not None:
                return self.consumer.last_stats
            return {}

        @self.get(f"{self.api_router_prefix}/info", response_class=JSONResponse)
        def get_service_info():
            """Get the service info"""
            hosts = {}
            assignments = {}
            lags = {}
            if self.consumer is not None:
                hosts = self.consumer.get_group_members()
                assignments = self.consumer.assigned_partitions
                lags = self.consumer.get_group_lag()
            return {
                "started": self._started,
                "app": {
                    "name": self.app_name,
                    "title": self.title,
                    "description": self.description,
                    "version": self.version,
                },
                "host": socket.gethostbyname(socket.gethostname()),
                "topics": {
                    "in": [
                        t.info(lags, assignments)
                        for t in self.topics.values()
                        if t.topic_dir != TopicDir.OUTPUT
                    ],
                    "out": [
                        t.info()
                        for t in self.topics.values()
                        if t.topic_dir != TopicDir.INPUT
                    ],
                },
                "agents": [a.info() for a in self.agents.values()],
                "websocket_agents": [a.info() for a in self.websocket_agents.values()],
                "hosts": {f"{tp[0]}-{tp[1]}": h for tp, h in hosts.items()},
            }

    def is_sink(self) -> bool:
        return self.app_type == AppType.SINK

    def fast_status(self) -> bool:
        """Return the status without actively checking Kafka connectivity"""

        # Check Kafka consumer error
        if self.consumer is not None:
            if self.consumer.kafka_error is not None:
                return False

        # Check Kafka producer error
        if self.producer is not None:
            if self.producer.kafka_error is not None:
                return False

        # Check background thread status
        if self.background_thread is not None:
            if not self.background_thread.is_alive():
                return False

        # Check consumer task status
        if self.main_consumer_loop_task is not None:
            if self.main_consumer_loop_task.done():
                return False

        # Check consumer task status
        if self.monitor_loop_task is not None:
            if self.monitor_loop_task.done():
                return False

        return True

    def status(self) -> bool:
        """Return the status, plus actively checking Kafka connectivity"""

        if not self.fast_status():
            return False

        if self.consumer is not None:
            # Use list topics to see if the broker is still up
            try:
                self.consumer.get_all_broker_topics()
            except KafkaException:
                logger.error("Failed to get topics from broker")
                return False

        if self.producer is not None:
            # Use list topics to see if the broker is still up
            try:
                self.producer.get_all_broker_topics()
            except KafkaException:
                logger.error("Failed to get topics from broker")
                return False
        return True

    def startup(self):
        """CitizenK startup. Called on FastAPI startup"""
        logger.debug("CitizenK starting up...")

        # Find all consumer topics
        for agent in self.agents.values():
            self.consumer_topics.update({t.name for t in agent.topics})
            self.total_batch_size += agent.batch_size

        # Create and start consumer
        if len(self.consumer_topics) > 0:
            if self.app_type == AppType.SOURCE:
                raise CitizenKError("Trying to consume topics in a source app")
            self.consumer = KafkaAdapter(
                self.kafka_config,
                KafkaRole.CONSUMER,
                self.app_name,
                self.consumer_group_init_offset,
            )
            self.consumer.start_consumer(list(self.consumer_topics))

        # Create producer
        if self.app_type in [AppType.SOURCE, AppType.TRANSFORM]:
            self.producer = KafkaAdapter(self.kafka_config, KafkaRole.PRODUCER)

        # Check that all topics exist in broker
        broker = self.producer if self.consumer is None else self.consumer
        broker_topics = broker.get_all_broker_topics()
        for topic_name, topic in self.topics.items():
            if topic_name not in broker_topics:
                raise CitizenKError(f"Can't find topic {topic_name} in broker")
            # Set num partitions and replicas in topic. Might be useful...
            topic.partition_count = len(broker_topics[topic_name].partitions)
            topic.replica_count = len(broker_topics[topic_name].partitions[0].replicas)

        # Start Main consumer loop if there is any consumer
        # Normal global consumer (with group)
        # Websocket consumers (no group)
        if self.consumer is not None or len(self.websocket_agents) > 0:

            if self.agents_in_thread:
                # Start in a thread
                self.background_loop = asyncio.new_event_loop()
                self.background_thread = threading.Thread(
                    target=self.background_consumer_thread, args=(self.background_loop,)
                )
                self.background_thread.start()
                self.main_consumer_loop_task = asyncio.run_coroutine_threadsafe(
                    self._main_consumer_loop(), self.background_loop
                )
            else:
                # Start in a task
                self.main_consumer_loop_task = asyncio.create_task(
                    self._main_consumer_loop()
                )
            self.monitor_loop_task = asyncio.create_task(self._monitor_loop())

    def shutdown(self):
        """CitizenK shutdown called on FastAPI shutown"""
        logger.debug("CitizenK shutting down...")
        if self.consumer is not None:
            self.consumer.close()
            self.consumer = None
        if self.producer is not None:
            self.producer.close()
            self.producer = None
        for agent in self.websocket_agents.values():
            agent.close()
        if self.main_consumer_loop_task is not None:
            self.main_consumer_loop_task.cancel()
        if self.background_loop is not None:
            self.background_loop.stop()

    def background_consumer_thread(self, loop: asyncio.BaseEventLoop):
        logger.debug("CitizenK background consumer thread started...")
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        except asyncio.CancelledError as e:
            logger.error("Background consumer loop cancelled %s", e)
        finally:
            for task in asyncio.all_tasks():
                logger.info("Stopping %s", task.get_name())
                task.cancel()
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.stop()
            loop.close()

    async def _monitor_loop(self):
        """Periodic task that checks Kafka status, and kills the process"""
        logger.debug("CitizenK main monitor loop started...")
        while True:
            await asyncio.sleep(10)
            # Check status
            if not self.status():
                self.shutdown()
                os.kill(os.getpid(), signal.SIGINT)
                await asyncio.sleep(60)
                os.kill(os.getpid(), signal.SIGKILL)

    async def _main_consumer_loop(self):
        """Main Kafka consumer loop which invokes the process agents"""
        logger.debug("CitizenK main processing loop started...")
        while True:
            # Check if consumer was deleted
            if self.consumer is None and len(self.consumer_topics) > 0:
                break

            try:
                start_time = time.time()
                processed = False
                # Consume from global consumer
                if self.consumer is not None:
                    msgs = self.consumer.consume(
                        num_messages=self.total_batch_size, timeout=0.1
                    )
                    if len(msgs) > 0:
                        processed = True
                        events = Agent.validate_messages(msgs, self.topics)
                        for agent in self.agents.values():
                            await agent.process(events)

                # Consume from websocket agents consumers (no group)
                for agent in self.websocket_agents.values():
                    if await agent.consume():
                        processed = True

                duration = 1000 * (time.time() - start_time)

                if duration > self.max_processing_cycle_ms:
                    logger.error(
                        "Processing cycle took %s ms > %s",
                        duration,
                        self.max_processing_cycle_ms,
                    )

                # Poll producer
                if self.producer is not None:
                    self.producer.poll()

                if processed:
                    # Just to give other tasks opportunity to run
                    await asyncio.sleep(0)
                else:
                    # Wait a bit until messages arrive
                    logger.debug("No kafka events, sleeping")
                    await asyncio.sleep(1)

            except Exception as e:
                logger.exception("Exception in main loop: %s", str(e))
                await asyncio.sleep(3)

    def topic(
        self,
        name: str,
        value_type: BaseModel,
        topic_dir: TopicDir = TopicDir.INPUT,
        subject_name: Optional[str] = None,
        partitioner: Callable[[Union[str, bytes]], int] = None,
    ) -> Topic:
        if name in self.topics:
            raise CitizenKError(f"Topic {name} already exists")
        t = Topic(
            self,
            name=name,
            value_type=value_type,
            topic_dir=topic_dir,
            subject_name=subject_name,
            partitioner=partitioner,
        )
        self.topics[name] = t
        logger.debug("Adding topic %s", name)
        return t

    def agent(
        self,
        topics: Union[Topic, List[Topic]],
        batch_size: int = 1,
        websocket_route: Optional[str] = None,
    ) -> Callable:
        """
        decorates a function of this type:
        async def processing_agent(events: List[KafkaEvent])

        Or this type:
        async def processing_agent(values: List[BaseModel])

        Both of these functions consumes from in_topics and produce to out_topics
        """

        if isinstance(topics, Topic):
            topics = [topics]

        def decorator(f):
            @wraps(f)
            async def wrapper(*args, **kwargs):
                return await f(*args, **kwargs)

            agent_name = f.__name__
            if "values" in signature(f).parameters:
                return_type = "values"
            elif "events" in signature(f).parameters:
                return_type = "events"
            else:
                raise CitizenKError("Agents can only accept values and events")
            if websocket_route is None:
                self.agents[agent_name] = Agent(
                    self, agent_name, f, topics, batch_size, return_type
                )
            else:
                self.websocket_agents[agent_name] = WebSocketAgent(
                    self,
                    agent_name,
                    f,
                    topics,
                    batch_size,
                    return_type,
                    websocket_route,
                )

            logger.debug("Adding agent %s %s", agent_name, topics)
            return wrapper

        return decorator

    def topic_router(self, topic: Topic, match_info: str) -> Callable:
        """
        routes the request to the right worker based on topic, key:
        assumes default partitioner... Used mainly for statefule services where
        Each worker holds some state / key
        """

        def decorator(f):
            @wraps(f)
            async def wrapper(*args, **kwargs):
                if self.consumer is None or self.consumer.consumer_group_name is None:
                    raise CitizenKError(
                        "Topic routing doesn't make sense without a consumer group"
                    )

                if "request" not in kwargs or not isinstance(
                    kwargs["request"], Request
                ):
                    raise CitizenKError(
                        "Topic routing endpoint must include a request object"
                    )

                if match_info is not None and match_info not in kwargs:
                    raise CitizenKError(
                        "Topic routing endpoint must include the match_info key"
                    )

                # Try to convert key to string... to support int as well
                key = str(kwargs[match_info])
                # Get the partition for this key and topic
                if topic.partitioner is not None:
                    partition_id = topic.partitioner(key)
                else:
                    partition_id = self.consumer.get_partition_id(topic.name, key)
                if partition_id is None:
                    raise CitizenKError("Failed to get partition id from key")

                logger.debug(
                    "Partition id for topic %s and key %s is %s",
                    topic.name,
                    key,
                    partition_id,
                )

                # Check if this worker is assigned to this partition
                if topic.name in self.consumer.assigned_partitions:
                    if partition_id in self.consumer.assigned_partitions[topic.name]:
                        return await f(*args, **kwargs)

                members = self.consumer.get_group_members()
                host = members.get((topic.name, partition_id), None)
                if host is None:
                    raise CitizenKError(
                        f"Can't find a host for this request {topic.name}/{partition_id}"
                    )

                # Route the request to the host
                request = kwargs["request"]
                params = dict(request.query_params)
                if "citizenk_stop_propogate" in params:
                    return await f(*args, **kwargs)
                params["citizenk_stop_propogate"] = True

                url = httpx.URL(str(request.url)).copy_with(host=host)
                # Mainly used for testing purposes
                if self.api_port is not None:
                    url = url.copy_with(port=self.api_port)
                logger.debug("Routing request to %s", url)
                async with httpx.AsyncClient() as client:
                    r = await client.request(
                        method=request.method,
                        url=url,
                        headers=request.headers.raw,
                        params=params,
                        content=await request.body(),
                        timeout=10.0,
                    )
                    try:
                        return r.json()
                    except json.JSONDecodeError:
                        return r.text

            return wrapper

        return decorator

    def broadcast_router(self) -> Callable:
        """
        routes the request to the all the workers and aggregate the JSON response
        """

        def decorator(f):
            @wraps(f)
            async def wrapper(*args, **kwargs):
                if self.consumer is None or self.consumer.consumer_group_name is None:
                    raise CitizenKError(
                        "Broadcast routing doesn't make sense without a consumer group"
                    )

                if "request" not in kwargs or not isinstance(
                    kwargs["request"], Request
                ):
                    raise CitizenKError(
                        "Broadcast routing endpoint must include a request object"
                    )

                members = self.consumer.get_group_members()
                hosts = set(members.values())

                # Route the request to the host
                request = kwargs["request"]
                params = dict(request.query_params)
                if "citizenk_stop_propogate" in params:
                    return await f(*args, **kwargs)
                params["citizenk_stop_propogate"] = True

                response = {}
                async with httpx.AsyncClient() as client:
                    for host in hosts:
                        url = httpx.URL(str(request.url)).copy_with(host=host)
                        # Mainly used for testing purposes
                        if self.api_port is not None:
                            url = url.copy_with(port=self.api_port)
                        logger.debug("Broadcast to %s", url)
                        r = await client.request(
                            method=request.method,
                            url=url,
                            headers=request.headers.raw,
                            params=params,
                            content=await request.body(),
                            timeout=10.0,
                        )
                        response[host] = r.json()
                return response

            return wrapper

        return decorator

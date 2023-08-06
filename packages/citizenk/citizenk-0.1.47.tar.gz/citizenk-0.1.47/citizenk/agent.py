from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, List

from confluent_kafka import Message as ConfluentMessage
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from .kafka_adapter import KafkaAdapter, KafkaRole
from .topic import Topic, TopicDir
from .utils import CitizenKError, annotate_function

if TYPE_CHECKING:
    from .citizenk import CitizenK

logger = logging.getLogger(__name__)


@dataclass
class KafkaEvent:
    key: str | bytes
    value: BaseModel
    topic: Topic
    partition: int
    offset: int
    timestamp: int
    headers: list[tuple[str, Any]]


class Agent:
    def __init__(
        self,
        app: CitizenK,
        name: str,
        coroutine: Callable,
        topics: list[Topic],
        batch_size: int = 1,
        return_type: str = "events",
    ):
        self.app = app
        self.name = name
        self.coroutine = coroutine
        self.topics = topics
        for topic in self.topics:
            if topic.topic_dir == TopicDir.OUTPUT:
                raise CitizenKError("Trying to consume from an output topic")

        self.topic_names = [t.name for t in self.topics]
        self.batch_size = batch_size
        self.return_type = return_type
        self.cycles = 0
        if self.app.auto_generate_apis:
            self._generate_apis()

    def info(self) -> dict[str, Any]:
        return {"name": self.name, "cycles": self.cycles}

    def _generate_apis(self):
        for topic in self.topics:

            async def endpoint(values: int):
                result = await self.coroutine(values=values)
                return result

            annotate_function(
                endpoint,
                name=f"send_to_agent_{self.name}_from_{topic.name}",
                doc=f"This endpoint sends value to agent {self.name} from topic {topic.name}",
                argument_types={"values": List[topic.value_type]},
            )

            self.app.add_api_route(
                path=f"{self.app.api_router_prefix}/agent/{self.name}/{topic.name}",
                response_class=JSONResponse,
                methods=["POST"],
                endpoint=endpoint,
            )

    @staticmethod
    def validate_messages(
        msgs: list[ConfluentMessage], topics: dict[str, Topic]
    ) -> list[KafkaEvent]:
        """Validate the incoming Kafka messages"""
        events = []
        for msg in msgs:
            topic_name = msg.topic()
            topic = topics[topic_name]
            try:
                value = topic.value_type(**json.loads(msg.value()))
            except json.decoder.JSONDecodeError as e:
                logger.error("For now, CitizenK only supports JSON values %s", e)
                continue
            except ValidationError as e:
                logger.error("Error while validating received value %s", e.json())
                continue

            events.append(
                KafkaEvent(
                    key=msg.key(),
                    value=value,
                    topic=topic,
                    partition=msg.partition(),
                    offset=msg.offset(),
                    timestamp=msg.timestamp()[1],
                    headers=msg.headers(),
                )
            )
        return events

    async def process(self, events: list[KafkaEvent]):
        filtered = []
        for event in events:
            if event.topic.name in self.topic_names:
                if self.return_type == "events":
                    filtered.append(event)
                else:
                    filtered.append(event.value)
        if len(filtered) > 0:
            self.cycles += 1
            arguments = {self.return_type: filtered}
            result = await self.coroutine(**arguments)
            return result
        return None

    def __str__(self) -> str:
        return self.name


class WebSocketAgent(Agent):
    def __init__(
        self,
        app: CitizenK,
        name: str,
        coroutine: Callable,
        topics: list[Topic],
        batch_size: int = 1,
        return_type: str = "events",
        websocket_route: str | None = None,
    ):
        Agent.__init__(
            self,
            app=app,
            name=name,
            coroutine=coroutine,
            topics=topics,
            batch_size=batch_size,
            return_type=return_type,
        )
        self.websocket_route = websocket_route
        if websocket_route:
            self._add_websocket_route()
        self.active_websocket_connections: list[WebSocket] = []
        self.consumer = None

    def _add_websocket_route(self):
        """Add FastAPI websocket route"""

        @self.app.websocket(self.websocket_route)
        async def w(websocket: WebSocket):
            await websocket.accept()
            self.active_websocket_connections.append(websocket)
            self._handle_consumer()
            try:
                while True:
                    # At the moment there is only support Kafka server --> Websocket client
                    # For clinet --> Kafka use REST API
                    data = await websocket.receive_text()
                    logger.info("Received data from we socket %s: ignoring", data)
            except WebSocketDisconnect:
                self.active_websocket_connections.remove(websocket)
                self._handle_consumer()

    def info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "cycles": self.cycles,
            "connections": len(self.active_websocket_connections),
        }

    def _handle_consumer(self):
        if len(self.active_websocket_connections) > 0 and self.consumer is None:
            # Start consumer once there is at least one connection
            # No consumer group, by default consumes from all partitions latest
            # TODO: support initial offset = latest - timedelta
            self.consumer = KafkaAdapter(self.app.kafka_config, KafkaRole.CONSUMER)
            self.consumer.start_consumer(topics=self.topic_names)
            logger.debug("Started agent %s consumer", self.name)
        if len(self.active_websocket_connections) == 0 and self.consumer is not None:
            # Close consumer if there are no live connections...
            self.consumer.close()
            self.consumer = None
            logger.debug("Closed agent %s consumer", self.name)

    async def consume(self):
        if self.consumer is not None:
            msgs = self.consumer.consume(num_messages=self.batch_size, timeout=0.1)
            if len(msgs) > 0:
                logger.debug("Agent %s consumed %s messages", self.name, len(msgs))
                events = Agent.validate_messages(msgs, {t.name: t for t in self.topics})
                await self.process(events)
                return True
        return False

    async def close(self):
        if self.consumer is not None:
            self.consumer.close()
            self.consumer = None
        for connection in self.active_websocket_connections:
            await connection.close()

    def _generate_apis(self):
        for topic in self.topics:

            async def endpoint(values: int):
                result = await self.coroutine(values=values)
                await self.websocket_broadcast_result(result)
                return result

            annotate_function(
                endpoint,
                name=f"send_to_websocket_agent_{self.name}_from_{topic.name}",
                doc=f"This endpoint sends value to agent {self.name} from topic {topic.name}",
                argument_types={"values": List[topic.value_type]},
            )

            self.app.add_api_route(
                path=f"{self.app.api_router_prefix}/agent/{self.name}/{topic.name}",
                response_class=JSONResponse,
                methods=["POST"],
                endpoint=endpoint,
            )

    async def websocket_broadcast_result(self, result: str):
        """Broadcast the agent result to all clients"""
        if result is None:
            return
        # Todo, consider using websocket.broadcast
        for connection in list(self.active_websocket_connections):
            try:
                await connection.send_text(result)
            except WebSocketDisconnect:
                logger.info("Websocket connection disconnected")
                self.active_websocket_connections.remove(connection)

    async def process(self, events: list[KafkaEvent]):
        """Process incoming events"""
        result = await Agent.process(self, events)
        await self.websocket_broadcast_result(result)
        return result

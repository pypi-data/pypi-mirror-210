import json
import logging
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import certifi
from confluent_kafka import (
    Consumer,
    KafkaError,
    KafkaException,
    Message,
    Producer,
    TopicPartition,
)
from confluent_kafka.admin import AdminClient, NewTopic

from .murmur2 import murmur2_partition

logger = logging.getLogger(__name__)


class KafkaRole(Enum):
    ADMIN = 1
    CONSUMER = 2
    PRODUCER = 3


@dataclass
class KafkaConfig:
    """Kafka connection details"""

    bootstrap_servers: str
    tls: bool = True
    sasl_mechanism: str = "PLAIN"
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    extra_config: Optional[Dict[str, str]] = None


class KafkaAdapter:
    """Kafka adapter Using confluent API"""

    def __init__(
        self,
        config: KafkaConfig,
        role: KafkaRole = KafkaRole.ADMIN,
        consumer_group_name: Optional[str] = None,
        consumer_group_init_offset: Optional[str] = "latest",
    ):
        self.role = role
        self.consumer_group_name = consumer_group_name
        self.consumer_started = False
        self.consumer_topics = {}
        self.assigned_partitions = defaultdict(set)
        self.kafka_error = None
        self.last_stats = {}
        self.topic_stats = defaultdict(int)

        self.sasl_username = config.sasl_username
        self.sasl_password = config.sasl_password
        self.sasl_mechanism = config.sasl_mechanism.upper()
        if self.sasl_mechanism == "PLAIN":
            self.config = {"security.protocol": "SSL" if config.tls else "PLAINTEXT"}
        elif self.sasl_mechanism in ["SCRAM-SHA-512", "SCRAM-SHA-256"]:
            if config.sasl_username is None or config.sasl_password is None:
                raise ValueError("Expected valid sasl_username and sasl_password")

            self.config = {
                "sasl.mechanism": self.sasl_mechanism,
                "security.protocol": "SASL_SSL" if config.tls else "SASL_PLAINTEXT",
                "ssl.ca.location": certifi.where(),
                "sasl.username": config.sasl_username,
                "sasl.password": config.sasl_password,
                "statistics.interval.ms": 15 * 60 * 1000,
                "error_cb": self._on_kafka_error,
                "stats_cb": self._on_kafka_stats,
            }
        else:
            raise ValueError("Unsupported sasl_mechanism")
        self.config["bootstrap.servers"] = config.bootstrap_servers
        if config.extra_config is not None:
            self.config.update(config.extra_config)

        self.admin_config = self.config.copy()
        if self.role == KafkaRole.CONSUMER:
            self.config["auto.offset.reset"] = consumer_group_init_offset
            self.config["on_commit"] = self._on_kafka_commit
            if self.consumer_group_name is not None:
                self.config["group.id"] = self.consumer_group_name
                self.config["enable.auto.commit"] = True
            else:
                logger.info("Starting consumer without a consumer group")
                self.config["enable.auto.commit"] = False
                self.config["group.id"] = "dummy_shouldnt_be_used"
            self.connection = Consumer(self.config, logger=logger)
        elif self.role == KafkaRole.PRODUCER:
            self.config["partitioner"] = "murmur2"
            self.connection = Producer(self.config, logger=logger)
        else:
            self.connection = AdminClient(self.admin_config)
        metadata = self.connection.list_topics(timeout=10)
        logger.debug("Connected to %s cluster %s", self.role.name, metadata.cluster_id)

    def get_all_broker_groups(self) -> List[str]:
        connection = AdminClient(self.admin_config)
        future = connection.list_consumer_groups(request_timeout=10)
        try:
            groups = future.result()
        except KafkaException:
            logger.error("Failed to get consumer groups")
            return []
        return [g.group_id for g in groups.valid]

    def get_group_members(self, groups: Optional[List[str]] = None) -> Dict[Tuple, str]:
        connection = AdminClient(self.admin_config)
        if groups is None:
            if self.consumer_group_name is None:
                return {}
            groups = [self.consumer_group_name]
        members = {}
        future_map = connection.describe_consumer_groups(groups, request_timeout=10)
        for future in future_map.values():
            try:
                g = future.result()
                for member in g.members:
                    if member.assignment:
                        host = member.host.split("/")[1]
                        for t in member.assignment.topic_partitions:
                            members[(t.topic, t.partition)] = host

            except KafkaException:
                logger.error("Error while describing group")
        return members

    def get_partition_id(self, topic: str, key: Union[str, bytes]) -> int:
        if isinstance(key, str):
            key = key.encode()
        num_partitions = self.get_partition_count(topic)
        if num_partitions == 0:
            return None
        return murmur2_partition(key, num_partitions)

    def get_partition_count(self, topic) -> int:
        """Get list of all topics in the broker"""
        topics = self.connection.list_topics(topic, timeout=10).topics
        if len(topics) == 0:
            return 0
        else:
            return len(topics[topic].partitions)

    def get_all_broker_topics(self) -> Dict[str, Any]:
        """Get list of all topics in the broker"""
        topics = self.connection.list_topics(timeout=10).topics
        return {
            topic_name: topic
            for topic_name, topic in topics.items()
            if not topic_name.startswith("__")
        }

    def get_all_broker_partitions(self) -> List[TopicPartition]:
        """Get list of all partiotions in the broker"""
        topics = self.get_all_broker_topics()
        return [
            TopicPartition(topic_name, p)
            for topic_name, topic in topics.items()
            for p in topic.partitions
        ]

    def get_partitions_with_offsets(
        self,
        topics: List[str],
        strategy: str = "latest",
        x: int = 0,
        epoch: int = 0,
        partition_filter: List[int] = [],
    ) -> List[TopicPartition]:
        """
        Get a list of partitions in the broker for the given topics
        And set offsets based on the specified strategy:
            p = num partitions
            latest-x/p
            earielst+x/p
            x
            time
        """
        filtered_partitions = []
        for topic in topics:
            # Get the topic's partitions
            metadata = self.connection.list_topics(topic, timeout=10)
            if metadata.topics[topic].error is not None:
                raise KafkaException(metadata.topics[topic].error)

            # Construct TopicPartition list of partitions to query
            if len(partition_filter) == 0:
                partitions = [
                    TopicPartition(topic, p) for p in metadata.topics[topic].partitions
                ]
            else:
                partitions = [
                    TopicPartition(topic, p)
                    for p in metadata.topics[topic].partitions
                    if p in partition_filter
                ]
            filtered_partitions += partitions

        # for time strategy lookup offset for time
        if strategy == "time":
            epoch = int(epoch)
            for p in filtered_partitions:
                p.offset = epoch
            return self.connection.offsets_for_times(filtered_partitions, timeout=10)
        else:
            for p in filtered_partitions:
                (lo, hi) = self.connection.get_watermark_offsets(
                    p, timeout=10, cached=False
                )
                if strategy == "latest":
                    p.offset = hi - x
                elif strategy == "earliest":
                    p.offset = lo + x
                elif strategy == "specific":
                    p.offset = x
                else:
                    raise ValueError("Unsupported offset strategy")

                if p.offset < lo:
                    p.offset = lo
                if p.offset > hi:
                    p.offset = hi
            return filtered_partitions

    def create_topic(
        self, topic_name: str, num_partitions: int = 3, replication_factor: int = 1
    ):
        """Create a topic, Mainly used for testing"""
        if self.role != KafkaRole.ADMIN:
            logger.error("Attempt to create a topic not in an admin role")
            return

        new_topics = [
            NewTopic(
                topic=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )
        ]
        fs = self.connection.create_topics(new_topics)
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                logger.debug("Topic %s created", topic)
            except KafkaException as e:
                logger.error("Failed to create topic %s: %s", topic, e)

    def get_own_group_topics(self) -> List[str]:
        """Get a list of all the topics in the replicator consumer group"""
        if self.role != KafkaRole.CONSUMER or self.consumer_group_name is None:
            return []

        group_topics = set()
        partitions = self.get_all_broker_partitions()
        # Find which topic has stored offset for the group
        try:
            committed = self.connection.committed(partitions, timeout=10)
        except KafkaException as e:
            logger.error(
                "Failed to get group committed offsets %s %s",
                self.consumer_group_name,
                e,
            )
            return []

        for p in committed:
            if p.offset > 0:
                group_topics.add(p.topic)
        return list(group_topics)

    def get_group_lag(self) -> Dict[str, int]:
        """Get the total lag of the group for each topic"""
        group_topics = defaultdict(int)
        if self.role != KafkaRole.CONSUMER or self.consumer_group_name is None:
            return group_topics

        partitions = self.get_all_broker_partitions()
        try:
            committed = self.connection.committed(partitions, timeout=10)
            for p in committed:
                if p.offset >= 0:
                    (_, hi) = self.connection.get_watermark_offsets(
                        p, timeout=10, cached=False
                    )
                    if hi < 0:
                        continue
                    topic = p.topic
                    lag = hi - p.offset
                    group_topics[topic] += lag
            logger.debug(
                "Topics Lag for %s group are %s", self.consumer_group_name, group_topics
            )
        except KafkaException as e:
            logger.error(
                "Failed to get group committed offsets %s %s",
                self.consumer_group_name,
                e,
            )
            return group_topics

        return group_topics

    def delete_groups(self, groups: List[str]) -> int:
        current_groups = self.get_all_broker_groups()
        count = 0
        for group in groups:
            if group in current_groups:
                self.delete_offset_for_group(group)
                count += 1
        return count

    def delete_offset_for_group(self, group: str, topic: Optional[str] = None) -> int:
        """
        Delete the offset of a topic for the group. If topic is not given,
        deletes the entire group
        """
        # When we stop replicating a topic, we want to delete the offsets of the consumer group
        # So that when we replicate the same topic back, we will start from latest and not the stored
        # offset. I coulnd't find a way to delete the offsets using the API, so I had to use the
        # Standard kafka cli for this
        # kafka-consumer-groups.sh --bootstrap-server 'localhost:9092' --group replicator --command-config local.config --topic globalvia.ap53.dev.camera.video.ocr - 1  --delete-offsets
        temp_config_filename = tempfile.NamedTemporaryFile(
            suffix=".config", delete=False
        ).name

        config_string = "\n".join([f"{k}={v}" for k, v in self.config.items()])
        if self.sasl_mechanism == "PLAIN":
            config_string += "\nsasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule"
            config_string += f' required username="{self.sasl_username}" password="{self.sasl_password}";'
        elif self.sasl_mechanism in ["SCRAM-SHA-512", "SCRAM-SHA-256"]:
            config_string += "\nsasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule"
            config_string += f' required username="{self.sasl_username}" password="{self.sasl_password}";'

        # This will also add some unknown configs like group.id, auto.offset.reset etc..
        with open(temp_config_filename, "w") as f:
            f.write(config_string)

        command = "kafka-consumer-groups.sh"
        params = {
            "--bootstrap-server": self.config["bootstrap.servers"],
            "--command-config": temp_config_filename,
            "--group": group,
        }
        if topic is None:
            params["--delete"] = ""
        else:
            params["--delete-offsets"] = ""
            params["--topic"] = topic

        command_with_params = command + "".join(
            [f" {k} {v}" for k, v in params.items()]
        )
        error_code = subprocess.call(
            command_with_params,
            shell=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
            timeout=15,
        )
        if error_code != 0:
            logger.error(
                "Failed to delete offsets for group using kafka CLI %s", error_code
            )
        if topic is None:
            logger.debug("Successfully deleted group %s", group)
        else:
            logger.debug(
                "Successfully deleted offsets for group %s topic %s", group, topic
            )
        os.remove(temp_config_filename)
        return error_code

    def delete_old_offsets_for_group(self) -> int:
        if self.role != KafkaRole.CONSUMER:
            return 0
        if not self.consumer_started:
            return 0
        if self.consumer_group_name is None:
            return 0
        # Check if the consumer group has unwanted topics if so, delete them
        count = 0
        group_topics = self.get_own_group_topics()
        for t in group_topics:
            if t not in self.consumer_topics:
                logger.info("topic %s is no longer replicated, deleting offsets", t)
                self.delete_offset_for_group(self.consumer_group_name, t)
                count += 1
        return count

    def start_consumer(
        self,
        topics: List[str],
        count: int = 0,
        strategy: str = "latest",
        epoch: int = 0,
        partition_filter: List[int] = [],
    ):
        """Start the consumer with the given topics. offset = latest-n"""
        self.stop_consumer()

        if self.consumer_group_name is not None:
            # Subscribe to desired source topics
            logger.debug("Subscribing to %s", topics)
            if len(topics) > 0:
                self.connection.subscribe(
                    topics,
                    on_assign=self._on_kafka_assign,
                    on_revoke=self._on_kafka_revoke,
                    on_lost=self._on_kafka_lost,
                )
        else:
            # Assign partitions to consumer
            logger.debug("Subscribing to %s without a consumer group", topics)
            source_partitions = self.get_partitions_with_offsets(
                topics=topics,
                x=count,
                strategy=strategy,
                epoch=epoch,
                partition_filter=partition_filter,
            )
            if len(source_partitions) == 0:
                logger.error("Couldn't find any partitions to assign to")
            else:
                self.connection.assign(source_partitions)
        self.consumer_topics = topics
        self.consumer_started = True
        logger.debug("Finished setting up consumer, and starting consuming")

    @staticmethod
    def stringify_key(key):
        if key is None or isinstance(key, str):
            return key
        elif isinstance(key, bytes):
            return key.decode()
        else:
            logger.error("Unexpected key type %s", type(key))
            return str(key)

    @staticmethod
    def messages_to_dict(messages: List[Message]) -> List[Dict[str, Any]]:
        try:
            return [
                {
                    "topic": m.topic(),
                    "key": KafkaAdapter.stringify_key(m.key()),
                    "value": json.loads(m.value()),
                    "partition": m.partition(),
                    "offset": m.offset(),
                    "timestamp": m.timestamp()[1],
                }
                for m in messages
            ]
        except json.decoder.JSONDecodeError as e:
            logger.debug("JSON Decode error %s", e)
            return []

    def consume(self, num_messages: int = 1, timeout: float = 1.0) -> List[Message]:
        """Consume records from the topics"""
        confluent_msgs = self.connection.consume(num_messages, timeout)
        msgs = []
        for msg in confluent_msgs:
            error = msg.error()
            if error is None:
                msgs.append(msg)
            else:
                self._on_kafka_error(error)
            self.topic_stats[msg.topic()] += 1
        logger.debug("Consumed %s Kafka messages", len(msgs))
        return msgs

    def produce(
        self,
        topic: str,
        value: Any,
        key: Optional[Any] = None,
        partition: int = -1,
        headers: Optional[Dict[str, bytes]] = None,
    ):
        if not isinstance(key, bytes):
            key = str(key).encode()
        """Produce a message to the given topic"""
        self.topic_stats[topic] += 1
        self.connection.produce(
            topic, value=value, key=key, partition=partition, headers=headers
        )

    def _on_kafka_commit(self, err: KafkaError, partitions: List[TopicPartition]):
        logger.debug("Kafka committed %s %s", err, partitions)

    def _on_kafka_stats(self, json_str: str):
        self.last_stats = json.loads(json_str)

    def _on_kafka_error(self, err: KafkaError):
        self.kafka_error = err
        logger.error("Kafka error %s", err)

    def _on_kafka_assign(self, consumer, partitions: List[TopicPartition]):
        logger.info("Group rebalancing. Partitions assigned %s", partitions)
        for p in partitions:
            self.assigned_partitions[p.topic].add(p.partition)

    def _on_kafka_revoke(self, consumer, partitions: List[TopicPartition]):
        logger.info("Group rebalancing. Partition revoked %s", partitions)
        for p in partitions:
            self.assigned_partitions[p.topic].discard(p.partition)

    def _on_kafka_lost(self, consumer, partitions: List[TopicPartition]):
        logger.info("Group rebalancing. Partitions lost %s", partitions)
        for p in partitions:
            self.assigned_partitions[p.topic].discard(p.partition)

    def get_topic_stats(self) -> Dict[str, int]:
        result = self.topic_stats
        self.topic_stats = defaultdict(int)
        return result

    def messages_in_queue(self) -> int:
        if self.role != KafkaRole.PRODUCER:
            return 0
        return len(self.connection)

    def poll(self):
        """Poll the broker"""
        self.connection.poll(0.1)

    def stop_consumer(self):
        """Stop the consumer"""
        if self.role != KafkaRole.CONSUMER:
            return
        if not self.consumer_started:
            return
        if self.consumer_group_name is None:
            logger.debug("Unassign from all partitions")
            self.connection.unassign()
        else:
            logger.debug("Unsubscribe from all partitions")
            self.connection.unsubscribe()

    def stop_producer(self):
        """Stop the producer"""
        if self.role != KafkaRole.PRODUCER:
            return
        self.connection.flush(timeout=10)
        logger.debug("Flushed producer queue")

    def close(self):
        """Close the connection"""
        self.stop_consumer()
        self.stop_producer()
        if self.role == KafkaRole.CONSUMER:
            self.connection.close()

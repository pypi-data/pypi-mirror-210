from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from confluent_kafka.schema_registry import Schema, SchemaRegistryClient
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from .utils import CitizenKError, annotate_function

if TYPE_CHECKING:
    from .citizenk import CitizenK

logger = logging.getLogger(__name__)


class JSONSchema(BaseModel):
    class Config:
        # This allows adding new optional properites to the schema
        schema_extra = {"additionalProperties": False}


class TopicDir(Enum):
    INPUT = 1
    OUTPUT = 2
    BIDIR = 3


class Topic:
    def __init__(
        self,
        app: CitizenK,
        name: str,
        value_type: BaseModel,
        topic_dir: TopicDir = TopicDir.INPUT,
        subject_name: str | None = None,
        partitioner: Callable[[str | bytes], int] = None,
    ):
        self.app = app
        self.name = name
        self.value_type = value_type
        self.topic_dir = topic_dir
        self.subject_name = (
            f"{name}-value".lower() if subject_name is None else subject_name
        )
        self.schema_id = None
        self.partitioner = partitioner
        self.partition_count = None
        self.replica_count = None
        if self.app.auto_generate_apis:
            self._generate_apis()

        # Register topic schema
        self.manage_schema()

    def info(self, lags: dict[str, int] = {}, assignments: dict[str, list[int]] = {}):
        topic_info = {
            "name": self.name,
            "dir": self.topic_dir.name,
            "value": self.value_type.__name__,
            "subject": self.subject_name,
            "partitions": self.partition_count,
            "replicas": self.replica_count,
        }
        if self.name in lags:
            topic_info["lag"] = lags[self.name]
        if self.name in assignments:
            topic_info["assignments"] = assignments[self.name]
        return topic_info

    def _generate_apis(self):
        if self.topic_dir in [TopicDir.OUTPUT, TopicDir.BIDIR]:

            def f(value: int, key: str = ""):
                self.send(value, key)
                return value

            annotate_function(
                f,
                name=f"send_to_topic_{self.name}",
                doc=f"This endpoint send value to topic {self.name}",
                argument_types={"value": self.value_type},
            )
            self.app.add_api_route(
                path=f"{self.app.api_router_prefix}/topic/{self.name}",
                response_class=JSONResponse,
                methods=["POST"],
                endpoint=f,
            )

    def send(
        self,
        value: dict[Any, Any] | BaseModel,
        key: str | bytes = None,
        partition: int = -1,
    ):
        if self.app.is_sink():
            raise CitizenKError("Trying to produce in a sink app")
        if self.topic_dir == TopicDir.INPUT:
            raise CitizenKError("Trying to produce to an input topic")

        if isinstance(value, dict):
            try:
                value = self.value_type(**value)
            except ValidationError as e:
                logger.error("Error while validating send value %s", e.json())
                return False
        if not isinstance(value, BaseModel):
            raise CitizenKError("Value should be a pydantic model", value)
        if not isinstance(key, (str, bytes)):
            raise CitizenKError("Key should be a either a str or bytes", key)
        if self.partitioner is not None and partition == -1:
            partition = self.partitioner(key)
        # TODO: Add schema to headers
        self.app.producer.produce(
            topic=self.name, value=value.json(), key=key, partition=partition
        )
        return True

    def manage_schema(self):
        """Handle schema registry registration and validation"""
        # https://yokota.blog/2021/03/29/understanding-json-schema-compatibility/
        if self.app.schema_registry_url is not None:
            # Schema registration
            schema_registry_conf = {"url": self.app.schema_registry_url}
            schema_registry_client = SchemaRegistryClient(schema_registry_conf)
            schema = Schema(
                schema_str=self.value_type.schema_json(), schema_type="JSON"
            )
            if self.topic_dir != TopicDir.INPUT:
                schema_id = schema_registry_client.register_schema(
                    subject_name=self.subject_name, schema=schema
                )
                logger.info("Schema id registered for %s is %s", self.name, schema_id)
                self.schema_id = schema_id
            # Schema validation
            if self.topic_dir != TopicDir.OUTPUT:
                if not schema_registry_client.test_compatibility(
                    subject_name=self.subject_name, schema=schema
                ):
                    logger.error(
                        "Schema for %s is not compatible with the latest schema registry",
                        self.name,
                    )
                else:
                    logger.info(
                        "Schema for %s is compatible with the latest schema registry",
                        self.name,
                    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

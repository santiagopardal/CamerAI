import json
import os
from typing import Optional

from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from src.message_brokers.message_broker import MessageBrokerPublisher


class RabbitMQ(MessageBrokerPublisher):

    def __init__(self):
        self._credentials = PlainCredentials(
            username=os.environ.get('RABBIT_USER'),
            password=os.environ.get('RABBIT_PASSWORD')
        )
        self._connection_parameters = ConnectionParameters(
            host=os.environ.get('RABBIT_HOST'),
            credentials=self._credentials
        )
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None
        self._declared_exchanges = set()

    def publish(self, data: dict, routing_key: str, exchange: str, exchange_type: str = "direct"):
        if exchange not in self._declared_exchanges:
            self.channel.exchange_declare(exchange=exchange_type, exchange_type=exchange_type)
            self._declared_exchanges.add(exchange)

        body = json.dumps(data)
        self.channel.basic_publish(exchange=exchange_type, routing_key=routing_key, body=body)

    @property
    def channel(self) -> BlockingChannel:
        if not self._channel or self._channel.is_closed or not self._channel.is_open:
            self._channel = self.connection.channel()

        return self._channel

    @property
    def connection(self) -> BlockingConnection:
        if not self._connection or self._connection.is_closed or not self._connection.is_open:
            self._connection = BlockingConnection(self._connection_parameters)

        return self._connection


def get_rabbit_publisher() -> MessageBrokerPublisher:
    rabbit_publisher = RabbitMQ()
    yield rabbit_publisher

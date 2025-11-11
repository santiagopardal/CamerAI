import json
from typing import Optional, Generator

from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from src import config
from src.message_brokers.message_broker import MessageBrokerPublisher


settings = config.get_settings()


class RabbitMQ(MessageBrokerPublisher):
    def __init__(self):
        self._credentials = PlainCredentials(
            username=settings.rabbitmq_settings.USER,
            password=settings.rabbitmq_settings.PASSWORD.get_secret_value(),
        )
        self._connection_parameters = ConnectionParameters(
            host=settings.rabbitmq_settings.HOST, credentials=self._credentials
        )
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None
        self._declared_exchanges = set()

    def publish(self, data: dict, routing_key: str, exchange: str, exchange_type: str = ExchangeType.direct):
        if exchange not in self._declared_exchanges:
            self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
            self._declared_exchanges.add(exchange)

        body = json.dumps(data)
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)

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


def rabbit_publisher_generator() -> Generator[MessageBrokerPublisher, None, None]:
    rabbit_publisher = RabbitMQ()

    while True:
        yield rabbit_publisher


rabbit_generator = rabbit_publisher_generator()


def get_rabbit_publisher() -> MessageBrokerPublisher:
    return next(rabbit_generator)

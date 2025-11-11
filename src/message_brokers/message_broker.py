from typing import Protocol


class MessageBrokerPublisher(Protocol):
    def publish(self, data: dict, routing_key: str, exchange: str, exchange_type: str = "direct"): ...

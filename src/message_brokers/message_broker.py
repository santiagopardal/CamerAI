from abc import ABC, abstractmethod


class MessageBrokerPublisher(ABC):

    @abstractmethod
    def publish(self, data: dict, routing_key: str, exchange: str, exchange_type: str = "direct"):
        ...

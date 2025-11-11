from typing import Protocol


class EventsSubscriber(Protocol):
    def notify(self, event_type: str, publisher: object, **event_data): ...

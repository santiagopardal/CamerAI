from typing import Iterator, TypedDict

from src.events_managers.events_subscriber import EventsSubscriber


Subscription = TypedDict(
    "Subscription",
    {
        "publisher": object,
        "subscriber": EventsSubscriber
    }
)


class EventsManager:

    def __init__(self):
        self._subscriptions: dict[str, list[Subscription]] = {}

    def subscribe(self, subscriber: EventsSubscriber, event_type: str, publisher: object):
        if self._subscriptions.get(event_type, None) is None:
            self._subscriptions[event_type] = []
        
        registered = any(
            subscription["publisher"] == publisher and subscriber == subscriber
            for subscription in self._subscriptions[event_type]
        )
        
        if not registered:
            self._subscriptions[event_type].append(
                {
                    "publisher": publisher,
                    "subscriber": subscriber
                }
            )

    def unsubscribe(self, subscriber: EventsSubscriber, event_type: str, publisher: object = None):
        def should_remain(subscription: Subscription) -> bool:
            if publisher is None:
                return subscription["subscriber"] != subscriber
            
            return subscription["subscriber"] != subscriber or subscription["publisher"] != publisher
        
        self._subscriptions["event_type"] = [
            subscription
            for subscription in self._subscriptions.get(event_type, [])
            if should_remain(subscription)
        ]

    def notify(self, event_type: str, publisher: object, **event_data):
        subscriptions = self._subscriptions.get(event_type, [])
        
        for subscription in subscriptions:
            if subscription["publisher"] == publisher:
                subscriber = subscription["subscriber"]
                subscriber.notify(
                    event_type=event_type,
                    publisher=publisher,
                    **event_data
                )


def get_event_manager_context() -> Iterator[EventsManager]:
    manager = EventsManager()
    while True:
        yield manager


context = get_event_manager_context()


def get_events_manager() -> EventsManager:
    return next(context)

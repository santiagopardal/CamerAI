class Subscriber:
    def notify(self):
        pass


class Publisher:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, sub: Subscriber):
        """
        Adds a new subscriber to the list.
        :param sub: Subscriber to add.
        """
        self._subscribers.append(sub)

    def unsubscribe(self, sub: Subscriber):
        """
        Unsubscribes a subscriber if already subscribed.
        :param sub: Subscriber.
        """
        if sub in self._subscribers:
            self._subscribers.remove(sub)

    def _notify_subscribed(self):
        """
        Notifies all subscribed that a new frame is ready to be read.
        """
        for sub in self._subscribers:
            sub.notify()
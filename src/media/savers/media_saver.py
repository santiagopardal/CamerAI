from typing import Protocol


class MediaSaver(Protocol):
    def save(self, media):
        ...

from .observer import Observer
from src.constants import DBS


class NaiveObserver(Observer):
    def observe(self, frames: list) -> list:
        to_observe = [(frames[i - 1], frame) for i, frame in enumerate(frames, 1)]
        results = self._batch_movement_check(to_observe)
        frames_with_movement = []
        for i, movement in enumerate(results):
            if movement:
                frames_with_movement.append(frames[i])
                frames_with_movement.append(frames[i + 1])

        return frames_with_movement

    def frames_to_buffer(self) -> int:
        return DBS

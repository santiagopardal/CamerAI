from .observer import Observer
from src.constants import JUMP, DBS


class DontLookBackObserver(Observer):
    def __init__(self, model_factory, sensitivity: int):
        super().__init__(model_factory, sensitivity)
        self._recording = False
        self._last_two_frames = []

    def observe(self, frames: list) -> list:
        if self._last_two_frames:
            frames.insert(0, self._last_two_frames[-1])
            frames.insert(0, self._last_two_frames[-2])
        to_observe = [(frame, frames[i + 1]) for i, frame in enumerate(frames) if i % JUMP == 0 and i > 0]

        self._last_two_frames = [frames[-2], frames[-1]]

        results = self._batch_movement_check(to_observe)
        results = list(enumerate(results))

        frames_with_movement = []

        # Here i is shifted 1 to the left that's why frames[i * JUMP + j] instead of frames[(i - 1) * JUMP + j]
        for i, movement in results:
            if movement or self._recording:
                frames_with_movement += frames[i * JUMP:(i + 1) * JUMP]

            self._recording = movement        

        return frames_with_movement

    def frames_to_buffer(self) -> int:
        return DBS - 2 if self._last_two_frames else DBS

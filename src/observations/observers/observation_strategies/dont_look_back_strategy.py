from src.observations.observers.observation_strategies.observation_strategy import ObservationStrategy
from src.constants import JUMP


class DontLookBackObservationStrategy(ObservationStrategy):
    def __init__(self, observer):
        super().__init__(observer)
        self._recording = False
        self._last_two_frames = []

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and determines those in which there has been movement.
        :param frames: Frames to analyse.
        """
        to_observe = [*self._last_two_frames, *frames]
        to_observe = [(frame, frames[i + 1]) for i, frame in enumerate(to_observe) if i % JUMP == 0]

        self._last_two_frames = [frames[-2], frames[-1]]

        results = self._observer.batch_movement_check(to_observe)
        results = list(enumerate(results))

        frames_with_movement = []

        for i, movement in results[1:]:
            if movement:
                for j in range(JUMP):
                    frames_with_movement.append(frames[(i - 1) * JUMP + j])

                self._recording = True
            else:
                if self._recording:
                    for j in range(JUMP):
                        frames_with_movement.append(frames[(i - 1) * JUMP + j])

                    self._recording = False

        return frames_with_movement

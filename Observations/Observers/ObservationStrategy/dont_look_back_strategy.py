from Observations.Observers.ObservationStrategy.observation_strategy import ObservationStrategy
from constants import JUMP


class DontLookBackObservationStrategy(ObservationStrategy):
    def __init__(self, observer):
        super().__init__(observer)

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and determines those in which there has been movement.
        :param frames: Frames to analyse.
        """
        to_observe = [(frame, frames[i + 1]) for i, frame in enumerate(frames) if i % JUMP == 0]

        results = self._observer.batch_movement_check(to_observe)

        frames_with_movement = []
        recording = False

        for i, result in enumerate(results):
            if recording and i > 0:
                last_element = (i - 1) * JUMP + 1

                for j in range(1, JUMP):
                    frames_with_movement.append(frames[last_element + j])

            if result or (not result and recording):
                frames_with_movement.append(frames[i*JUMP])
                frames_with_movement.append(frames[i*JUMP+1])

            recording = result

        return frames_with_movement

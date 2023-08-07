from .observer import Observer
from src.constants import JUMP, DBS


class LookBackObserver(Observer):
    def observe(self, frames: list) -> list:
        to_observe = [(frame, frames[i + 1]) for i, frame in enumerate(frames) if i % JUMP == 0]

        results = self._batch_movement_check(to_observe)

        recording = False
        frames_list_length = len(frames)

        frames_with_movement = []

        for i, result in enumerate(results):
            if result:
                if not recording:
                    recording = True

                    if i != 0:
                        last_element = (i - 1) * JUMP + 1
                        j = i * JUMP - 1

                        found_no_movement = False

                        for j in range(j, last_element, -2):
                            frm = frames[j]
                            pframe = frames[j - 1]

                            if self._movement(pframe, frm):
                                frames_with_movement.append(frm)
                                frames_with_movement.append(pframe)
                            else:
                                frames_with_movement.append(frames[j])
                                found_no_movement = True
                                break

                        if not found_no_movement and j == last_element - 1:
                            frames_with_movement.append(frames[last_element - 1])
                else:
                    j = i * JUMP - 1
                    last_element = (i - 1) * JUMP + 2

                    for j in range(j, last_element, -1):
                        frames_with_movement.append(frames[j])

                frames_with_movement.append(frames[i * JUMP + 1])
                frames_with_movement.append(frames[i * JUMP])

                if i * JUMP + 2 < frames_list_length:
                    frames_with_movement.append(frames[i * JUMP + 2])
            else:
                if recording:
                    recording = False
                    store_all = False
                    j = i * JUMP - 1
                    last_element = (i - 1) * JUMP + 1

                    for j in range(j, last_element + 1, -2):
                        frm = frames[j]
                        pframe = frames[j - 1]

                        if self._movement(pframe, frm):
                            store_all = True
                            break

                    if store_all:
                        frames_with_movement.append(frames[j + 1])
                        for j in range(j, last_element, -2):
                            frames_with_movement.append(frames[j])
                            frames_with_movement.append(frames[j - 1])

        return frames_with_movement

    def frames_to_buffer(self) -> int:
        return DBS

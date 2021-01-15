import cv2
from Detectors.CNNs import create_main_model
from Cameras.Frame import Frame
import Constants
import numpy as np
import time
import tensorflow as tf


tf.config.optimizer.set_jit(True)


class Observer:
    def __init__(self):
        pass

    def observe(self, frames: list) -> list:
        return []


class MovementDetectionObserver(Observer):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)

        return cls.instance

    def __init__(self, nn=None):
        """
        :param nn: Neural network to detect movement, if not specified will use default.
        """
        super().__init__()

        if nn is None:
            self._neural_network = create_main_model()
        else:
            self._neural_network = nn

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and stores those in which there has been movement. Also checks whether
        it is time to switch observers and does so if needed.
        :param frames: Frames to analyse.
        """

        to_observe = [(frame, frames[i + 1]) for i, frame in enumerate(frames) if i % Constants.JUMP == 0]

        start = time.time()
        results = self._batch_movement_check(to_observe)

        recording = False
        bursts = 0
        looked = len(results)

        frames_with_movement = []

        for i, result in enumerate(results):
            if result:
                if not recording:
                    bursts += 1
                    recording = True

                    if i != 0:
                        last_element = (i - 1) * Constants.JUMP + 1
                        j = i * Constants.JUMP - 1

                        found_no_movement = False

                        while j > last_element and not found_no_movement:
                            frm = frames[j]
                            pframe = frames[j - 1]
                            looked += 1

                            if self._movement(pframe, frm):
                                frames_with_movement.append(frm)
                                frames_with_movement.append(pframe)
                            else:
                                frames_with_movement.append(frames[j])
                                found_no_movement = True

                            j = j - 2

                        if not found_no_movement and j == last_element - 1:
                            frames_with_movement.append(frames[last_element - 1])
                else:
                    j = i * Constants.JUMP - 1
                    last_element = (i - 1) * Constants.JUMP + 2

                    while j > last_element:
                        frames_with_movement.append(frames[j])
                        j = j - 1

                frames_with_movement.append(frames[i * Constants.JUMP + 1])
                frames_with_movement.append(frames[i * Constants.JUMP])

                if i * Constants.JUMP + 2 < len(frames):
                    frames_with_movement.append(frames[i * Constants.JUMP + 2])
            else:
                if recording:
                    recording = False
                    store_all = False
                    j = i * Constants.JUMP - 1
                    last_element = (i - 1) * Constants.JUMP + 1

                    while j - 1 > last_element and not store_all:
                        frm = frames[j]
                        pframe = frames[j - 1]
                        looked += 1
                        if self._movement(pframe, frm):
                            store_all = True
                        else:
                            j = j - 2

                    if store_all:
                        frames_with_movement.append(frames[j + 1])
                        while j > last_element:
                            frames_with_movement.append(frames[j])
                            frames_with_movement.append(frames[j - 1])
                            j = j - 2

        d = (time.time() - start)
        print("Looked at {} relative FPS and {} real FPS, {} times with {} bursts"
              .format(len(frames) / d, looked / d, looked, bursts))

        del to_observe
        del results

        return frames_with_movement

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        """
        Determines whether there has been movement between two frames.
        :param previous_frame: Frame more distant in time.
        :param frame: Frame nearest in time.
        :return: True if there is movement, False if there is not movement.
        """
        return self._batch_movement_check([(previous_frame, frame)])[0]

    def _frame_manipulation(self, frame: Frame) -> Frame:
        """
        Manipulates the frame, in other words, performs some operation to the frame.
        :param frame: Frame to manipulate.
        :return: Frame manipulated.
        """
        return frame

    def _prepare_for_cnn(self, pf: Frame, frm: Frame):
        """
        Creates and returns an NumPy array with the difference between pf and frm resized, grayscaled and normalized.
        :param pf: Frame more distant in time.
        :param frm: Frame nearest in time.
        :return: NumPy array with the difference between pf and frm resized, grayscaled and normalized.
        """
        pf = self._frame_manipulation(pf)
        pf = pf.get_resized_and_grayscaled()

        frm = self._frame_manipulation(frm)
        frm = frm.get_resized_and_grayscaled()

        diff = np.array(cv2.absdiff(pf, frm) / 255, dtype="float32").reshape(Constants.CNN_INPUT_SHAPE)

        return diff

    def _batch_movement_check(self, frames: list) -> list:
        """
        Returns a list with the results of checking for all difference in frames if there has been movement or not. By
        difference I mean what _prepare_for_cnn returns.
        :param frames: Frames to analyse.
        :return: List with boolean values representing whether there has been movement or not.
        """
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        movements = self._neural_network.predict_on_batch(np.array(images))

        del images

        return [movement[0] >= Constants.MOVEMENT_SENSITIVITY for movement in movements]


class DenoiserObserver(MovementDetectionObserver):
    """
    MovementDetectionObserver for when the night comes, it does the same as MovementDetectionObserver but denoises the frames
    before analysing.
    This observer is more useful for cameras with low image quality.
    """
    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame.get_denoised_frame()

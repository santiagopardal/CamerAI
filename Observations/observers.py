import cv2
from Detectors.CNNs import create_lite_model, create_tflite_interpreter
from Cameras.frame import Frame
import constants
import numpy as np
import tensorflow as tf


tf.config.optimizer.set_jit(True)


class Observer:
    def __init__(self):
        pass

    def _frame_manipulation(self, frame: Frame) -> Frame:
        """
        Manipulates the frame, in other words, performs some operation to the frame.
        :param frame: Frame to manipulate.
        :return: Frame manipulated.
        """
        return frame

    def _prepare_for_cnn(self, pf: Frame, frm: Frame) -> np.ndarray:
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

        return np.array(cv2.absdiff(pf, frm) / 255, dtype="float32").reshape(constants.CNN_INPUT_SHAPE)

    def _batch_movement_check(self, frames: list) -> list:
        pass

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        """
        Determines whether there has been movement between two frames.
        :param previous_frame: Frame more distant in time.
        :param frame: Frame nearest in time.
        :return: True if there is movement, False if there is not movement.
        """
        return self._batch_movement_check([(previous_frame, frame)])[0]

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and stores those in which there has been movement. Brace yourself.
        :param frames: Frames to analyse.
        """
        to_observe = [(frame, frames[i + 1]) for i, frame in enumerate(frames) if i % constants.JUMP == 0]

        results = self._batch_movement_check(to_observe)

        recording = False
        bursts = 0
        looked = len(results)
        frames_list_length = len(frames)

        frames_with_movement = []

        for i, result in enumerate(results):
            if result:
                if not recording:
                    bursts += 1
                    recording = True

                    if i != 0:
                        last_element = (i - 1) * constants.JUMP + 1
                        j = i * constants.JUMP - 1

                        found_no_movement = False

                        for j in range(j, last_element, -2):
                            frm = frames[j]
                            pframe = frames[j - 1]
                            looked += 1

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
                    j = i * constants.JUMP - 1
                    last_element = (i - 1) * constants.JUMP + 2

                    for j in range(j, last_element, -1):
                        frames_with_movement.append(frames[j])

                frames_with_movement.append(frames[i * constants.JUMP + 1])
                frames_with_movement.append(frames[i * constants.JUMP])

                if i * constants.JUMP + 2 < frames_list_length:
                    frames_with_movement.append(frames[i * constants.JUMP + 2])
            else:
                if recording:
                    recording = False
                    store_all = False
                    j = i * constants.JUMP - 1
                    last_element = (i - 1) * constants.JUMP + 1

                    for j in range(j, last_element + 1, -2):
                        frm = frames[j]
                        pframe = frames[j - 1]
                        looked += 1

                        if self._movement(pframe, frm):
                            store_all = True
                            break

                    if store_all:
                        frames_with_movement.append(frames[j + 1])
                        for j in range(j, last_element, -2):
                            frames_with_movement.append(frames[j])
                            frames_with_movement.append(frames[j - 1])

        del to_observe
        del results

        return frames_with_movement


class MovementDetectionObserver(Observer):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, nn=None):
        """
        :param nn: Neural network to detect movement, if not specified will use default.
        """
        super().__init__()

        if nn is None:
            self._neural_network = create_lite_model()
        else:
            self._neural_network = nn

    def _batch_movement_check(self, frames: list) -> list:
        """
        Returns a list with the results of checking for all difference in frames if there has been movement or not. By
        difference I mean what _prepare_for_cnn returns.
        :param frames: List of frames to analyse.
        :return: List with boolean values representing whether there has been movement or not.
        """
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        movements = self._neural_network(np.array(images))

        return [movement[0] >= constants.MOVEMENT_SENSITIVITY for movement in movements]


class LiteObserver(Observer):
    def __init__(self):
        super().__init__()

        self._interpreter = create_tflite_interpreter()

    def _prepare_for_cnn(self, previous_frame, frame):
        res = super()._prepare_for_cnn(previous_frame, frame)

        return np.expand_dims(res, axis=0)

    def _tflite_predict(self, image):
        self._interpreter.set_tensor(self._interpreter.get_input_details()[0]['index'], image)

        self._interpreter.invoke()

        output_data = self._interpreter.get_tensor(self._interpreter.get_output_details()[0]['index'])
        results = np.squeeze(output_data)

        return results

    def _batch_movement_check(self, frames: list) -> list:
        """
        Returns a list with the results of checking for all difference in frames if there has been movement or not. By
        difference I mean what _prepare_for_cnn returns.
        :param frames: List of frames to analyse.
        :return: List with boolean values representing whether there has been movement or not.
        """
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        return [self._tflite_predict(image) >= constants.MOVEMENT_SENSITIVITY for image in images]


class DenoiserObserver(MovementDetectionObserver):
    """
    DenoiserObserver does the same as MovementDetectionObserver but denoises the frames before analysing.
    This observer is more useful for cameras with low image quality.
    """
    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame.get_denoised_frame()

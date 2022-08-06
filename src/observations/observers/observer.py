import cv2
from src.media.frame import Frame
from src import constants
import numpy as np
from src.observations.observers.observation_strategies.dont_look_back_strategy import DontLookBackObservationStrategy
from src.observations.observers.observation_strategies.observation_strategy import ObservationStrategy


class Observer:
    def __init__(self, model_factory, observation_strategy: ObservationStrategy = None):
        self._model = model_factory.create_model()
        self._observation_strategy = DontLookBackObservationStrategy(self) if not observation_strategy else observation_strategy

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
        p_frame = self._frame_manipulation(pf)
        p_frame = p_frame.get_resized_and_grayscaled()

        frm = self._frame_manipulation(frm)
        frm = frm.get_resized_and_grayscaled()

        return np.array(cv2.absdiff(p_frame, frm) / 255, dtype="float32").reshape(constants.CNN_INPUT_SHAPE)

    def batch_movement_check(self, frames: list) -> list:
        """
        Returns a list with the results of checking for all difference in frames if there has been movement or not. By
        difference, I mean what _prepare_for_cnn returns.
        :param frames: List of frames to analyse.
        :return: List with boolean values representing whether there has been movement or not.
        """
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        movements = self._model.predict_on_batch(images)

        return [movement >= constants.MOVEMENT_SENSITIVITY for movement in movements]

    def movement(self, previous_frame: Frame, frame: Frame) -> bool:
        """
        Determines whether there has been movement between two frames.
        :param previous_frame: Frame more distant in time.
        :param frame: Frame nearest in time.
        :return: True if there is movement, False if there is no movement.
        """
        image = self._prepare_for_cnn(previous_frame, frame)

        return self._model.predict(image) >= constants.MOVEMENT_SENSITIVITY

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and stores those in which there has been movement.
        :param frames: Frames to analyse.
        """
        return self._observation_strategy.observe(frames)

    def frames_to_buffer(self) -> int:
        return self._observation_strategy.frames_to_buffer()

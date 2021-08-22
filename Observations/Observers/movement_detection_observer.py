from observer import Observer
from Detectors.CNNs import create_lite_model
import numpy as np
import constants


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
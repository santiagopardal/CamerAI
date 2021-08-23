from Observations.Observers.observer import Observer
from Observations.Models.TFLiteMovementDetector import TFLiteModelDetector
import numpy as np


class LiteObserver(Observer):
    def __init__(self):
        super().__init__(TFLiteModelDetector())

    def _prepare_for_cnn(self, previous_frame, frame):
        res = super()._prepare_for_cnn(previous_frame, frame)

        return np.expand_dims(res, axis=0)

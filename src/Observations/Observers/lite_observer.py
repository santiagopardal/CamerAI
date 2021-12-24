from src.Observations.Observers.observer import Observer
import numpy as np
from src.Media.frame import Frame
from threading import Lock
from src.Observations.Models.TFLiteMovementDetector import TFLiteModelDetector


class LiteObserver(Observer):
    _instance = None
    _model_process = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        super().__init__(TFLiteModelDetector())
        self._mutex = Lock()

    def _prepare_for_cnn(self, previous_frame, frame):
        res = super()._prepare_for_cnn(previous_frame, frame)

        return np.expand_dims(res, axis=0)

    def batch_movement_check(self, frames: list) -> list:
        self._mutex.acquire()
        res = super().batch_movement_check(frames)
        self._mutex.release()

        return res

    def movement(self, previous_frame: Frame, frame: Frame) -> bool:
        self._mutex.acquire()
        res = super().movement(previous_frame, frame)
        self._mutex.release()

        return res

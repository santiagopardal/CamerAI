from Observations.Observers.observer import Observer
from Observations.Models.TFLiteMovementDetector import TFLiteModelDetector
import numpy as np
from threading import Semaphore
from CameraUtils.frame import Frame


class LiteObserver(Observer):
    _instance = None
    _model = TFLiteModelDetector()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        super().__init__(self._model)
        self._mutex = Semaphore(1)

    def _prepare_for_cnn(self, previous_frame, frame):
        res = super()._prepare_for_cnn(previous_frame, frame)

        return np.expand_dims(res, axis=0)

    def _batch_movement_check(self, frames: list) -> list:
        self._mutex.acquire()
        res = super()._batch_movement_check(frames)
        self._mutex.release()

        return res

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        self._mutex.acquire()
        res = super()._movement(previous_frame, frame)
        self._mutex.release()

        return res

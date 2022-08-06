from src.observations.observers.dont_look_back_observer import DontLookBackObserver
import numpy as np
from src.media.frame import Frame
from threading import Lock
from src.observations.models.tflite_movement_detector import TFLiteModelDetector


class LiteObserver(DontLookBackObserver):
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

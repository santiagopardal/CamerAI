from Observations.Observers.observer import Observer
from Observations.Models.TFLiteMovementDetector import TFLiteModelDetector
import numpy as np
from threading import Semaphore
from CameraUtils.frame import Frame
from multiprocessing import Process, Manager
from Observations.Models.lite_model_process import process
import constants


class LiteObserver(Observer):
    _instance = None
    _model_process = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._model_process = cls.__create_model_process(cls._instance)
            cls._model_process.start()

        return cls._instance

    def __init__(self):
        super().__init__()

    def __create_model_process(cls):
        manager = Manager()
        cls._frames_for_process_to_observe = manager.Queue()
        cls._results = manager.Queue()

        cls._frames_for_process = manager.Semaphore(0)
        cls._results_from_process = manager.Semaphore(0)

        cls._done = manager.Value('i', False)

        return Process(target=process, args=(cls._frames_for_process, cls._results_from_process,
                                             cls._frames_for_process_to_observe, cls._results, cls._done))

    def _prepare_for_cnn(self, previous_frame, frame):
        res = super()._prepare_for_cnn(previous_frame, frame)

        return np.expand_dims(res, axis=0)

    def _batch_movement_check(self, frames: list) -> list:
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        self._frames_for_process_to_observe.put(images)
        self._frames_for_process.release()

        self._results_from_process.acquire()
        movements = self._results.get()

        for frame in frames:
            frame.clean_cache()

        return [movement >= constants.MOVEMENT_SENSITIVITY for movement in movements]

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        image = self._prepare_for_cnn(previous_frame, frame)

        self._frames_for_process_to_observe.put([image])
        self._frames_for_process.release()

        self._results_from_process.acquire()
        movement = self._results.get()[0]

        previous_frame.clean_cache()

        return movement >= constants.MOVEMENT_SENSITIVITY

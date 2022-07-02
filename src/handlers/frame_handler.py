from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Lock
import datetime
from src import constants
import numpy as np
import time
from src.media.frame import Frame
from src.observations.observers.observer import Observer
from src.handlers.handler import Handler
from src.observations.observers.dynamic_movement_detection_observer import DynamicMovementDetectionObserver
from src.handlers.motion_handler import MotionHandler


class FrameHandler(Handler):

    _observer: Observer
    _motion_handlers: list
    _thread_pool: ThreadPoolExecutor
    _current_buffer: list
    _current_buffer_started_receiving: float

    def __init__(self, observer: Observer = None, motion_handlers: list = None):
        super().__init__()
        self._observer = DynamicMovementDetectionObserver() if observer is None else observer
        self._motion_handlers = [] if motion_handlers is None else motion_handlers
        self._thread_pool = ThreadPoolExecutor(1)
        self._current_buffer = []
        self._current_buffer_started_receiving = 0.0
        self._lock = Lock()

    def start(self):
        """
        Starts the handler.
        """
        self._current_buffer_started_receiving = time.time()

    def stop(self):
        """
        Stops the handler.
        """
        self._thread_pool.shutdown()

        for handler in self._motion_handlers:
            handler.stop()

    def set_observer(self, observer: Observer):
        if observer:
            self._observer = observer

    def add_motion_handler(self, handler: MotionHandler):
        if handler:
            self._motion_handlers.append(handler)

    def set_motion_handlers(self, handlers: list):
        for handler in self._motion_handlers:
            handler.stop()

        self._motion_handlers.clear()

        for handler in handlers:
            self._motion_handlers.append(handler)

    def handle(self, frame: np.ndarray):
        """
        Handles a new frame.
        :param frame: Frame to handle.
        """
        self._lock.acquire()
        self._current_buffer.append(frame)

        if len(self._current_buffer) >= constants.DBS:
            end = time.time()

            true_framerate = len(self._current_buffer) / (end - self._current_buffer_started_receiving) \
                if self._current_buffer_started_receiving else constants.FRAME_RATE

            self._thread_pool.submit(self._check_movement, self._current_buffer, true_framerate)
            self._current_buffer = []
            self._current_buffer_started_receiving = end

        self._lock.release()

    @staticmethod
    def _calculate_time_taken(tme, frame_rate, i):
        """
        Approximates the time a frame was taken using the last time an image was received and the framerate.
        :param tme: Last time an image was received.
        :param frame_rate: Frame rate.
        :return: Time the frame was taken approximately.
        """
        return tme + datetime.timedelta(seconds=i / frame_rate)

    @staticmethod
    def _last_time_stored(frame_rate):
        return datetime.datetime.now() - datetime.timedelta(seconds=(constants.DBS + 1) / frame_rate)

    def _check_movement(self, frames, frame_rate):
        """
        Tells the observer to take a look at frames.

        Create frames and calculate the time they were taken, this is done here because obtaining the time
        takes a lot of CPU time and it's not worth doing while receiving the frames from the camera. Note that
        the first frame will be the same as the last of the previous batch, so we add the previous frame so as
        to not calculate everything again, including everything needed by the observer, so the last frame
        won't be analysed by the observer until the next batch arrives and will be the first frame of that
        batch. This does not occur on the first run, in which all the frames will be analysed and the last one
        will be analysed twice, on the first run and on the second one, but will be stored only once if needed.
        """
        last_time_stored = self._last_time_stored(frame_rate)

        frames = [Frame(frame, self._calculate_time_taken(last_time_stored, frame_rate, i + 1))
                  for i, frame in enumerate(frames)]

        movement = self._observer.observe(frames)

        for handler in self._motion_handlers:
            handler.handle(movement)

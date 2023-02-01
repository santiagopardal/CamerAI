from concurrent.futures import ThreadPoolExecutor
import datetime
from src import constants
import numpy as np
import time
from collections import deque
from src.media import Frame
from src.observations import Observer
from src.observations import DontLookBackObserver
import src.observations.models.factory as model_factory
from src.handlers import MotionHandler
import asyncio


class FrameHandler:
    def __init__(self, observer: Observer = None, motion_handlers: list = None):
        super().__init__()
        self._observer = DontLookBackObserver(model_factory, constants.MOVEMENT_SENSITIVITY) if observer is None else observer
        self._motion_handlers = [] if motion_handlers is None else motion_handlers
        self._thread_pool = ThreadPoolExecutor(1)
        self._buffer = deque()
        self._cleared_buffer = True
        self._current_buffer_started_receiving = 0.0

    def start(self):
        self._current_buffer_started_receiving = time.time()

    def stop(self):
        self._thread_pool.shutdown(True)

    def set_observer(self, observer: Observer):
        self._observer = observer

    def add_motion_handler(self, handler: MotionHandler):
        if handler:
            self._motion_handlers.append(handler)

    def set_motion_handlers(self, handlers: list):
        self._motion_handlers = handlers

    async def handle(self, frame: np.ndarray):
        self._buffer.append(frame)

        if self._cleared_buffer and len(self._buffer) >= self._observer.frames_to_buffer():
            self._cleared_buffer = False
            end = time.time()

            true_framerate = self._observer.frames_to_buffer() / (end - self._current_buffer_started_receiving) \
                if self._current_buffer_started_receiving else constants.FRAME_RATE

            asyncio.create_task(self._check_movement(true_framerate))
            self._current_buffer_started_receiving = end

    @staticmethod
    def _calculate_time_taken(tme, frame_rate, i):
        return tme + datetime.timedelta(seconds=i / frame_rate)

    @staticmethod
    def _last_time_stored(frame_rate: int, number_of_frames: int):
        return datetime.datetime.now() - datetime.timedelta(seconds=(number_of_frames + 1) / frame_rate)

    async def _check_movement(self, frame_rate):
        """
        Tells the observer to take a look at frames.

        Create frames and calculate the time they were taken, this is done here because obtaining the time
        takes a lot of CPU time and, it's not worth doing while receiving the frames from the camera. Note that
        the first frame will be the same as the last of the previous batch, so we add the previous frame
        to not calculate everything again, including everything needed by the observer, so the last frame
        won't be analysed by the observer until the next batch arrives and will be the first frame of that
        batch. This does not occur on the first run, in which all the frames will be analysed and the last one
        will be analysed twice, on the first run and on the second one, but will be stored only once if needed.
        """
        if len(self._buffer) >= self._observer.frames_to_buffer():
            frames = [self._buffer.popleft() for _ in range(self._observer.frames_to_buffer())]
            self._cleared_buffer = True
            last_time_stored = self._last_time_stored(frame_rate, len(frames))

            frames = [Frame(frame, self._calculate_time_taken(last_time_stored, frame_rate, i + 1))
                      for i, frame in enumerate(frames)]

            movement = self._observer.observe(frames)
            tasks = [handler.handle(movement) for handler in self._motion_handlers]
            await asyncio.gather(*tasks)

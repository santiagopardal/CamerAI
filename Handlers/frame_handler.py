import sys
from threading import Thread, Semaphore
import datetime
import constants
import numpy as np
import time
from collections import deque
from CameraUtils.frame import Frame
from Observations.Observers.observer import Observer
from Handlers.handler import Handler
from Observations.Observers.lite_observer import LiteObserver
from Handlers.motion_handler import MotionHandler


class FrameHandler(Handler):
    def __init__(self, observer: Observer = None, motion_handlers: list = None):
        super().__init__()

        self._observer = LiteObserver() if observer is None else observer
        self._motion_handlers = [] if motion_handlers is None else motion_handlers
        self._thread = None
        self._kill_thread = False
        self._observe_semaphore = Semaphore(0)
        self._frames_to_observe = deque()
        self._current_buffer = []
        self._current_buffer_started_receiving = None
        self._started = False

    def start(self):
        """
        Starts the handler.
        """
        if not self._started and not self._kill_thread:
            self._current_buffer_started_receiving = time.time()

            self._thread = Thread(target=self._check_movement, args=())
            self._thread.start()

            self._started = True

    def stop(self):
        """
        Stops the handler.
        """
        if self._started:
            self._kill_thread = True

            self._frames_to_observe.clear()
            self._current_buffer.clear()

            self._observe_semaphore.release()

            self._thread.join()
            self._started = False
            self._kill_thread = False

        for handler in self._motion_handlers:
            handler.stop()

        while self._observe_semaphore.acquire(blocking=False):
            continue

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
        if self._started and not self._kill_thread:
            self._current_buffer.append(frame)

            if len(self._current_buffer) >= constants.DBS:
                end = time.time()

                true_framerate = len(self._current_buffer) / (end - self._current_buffer_started_receiving) \
                    if self._current_buffer_started_receiving else constants.FRAMERATE

                self._frames_to_observe.append((self._current_buffer, true_framerate))
                self._observe_semaphore.release()
                self._current_buffer = []
                self._current_buffer_started_receiving = end

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

    def _check_movement(self):
        """
        Waits for images to be ready and tells the observer to take a look at them.
        """
        last_frame = None
        last_time_stored = None

        while not self._kill_thread:
            self._observe_semaphore.acquire()

            if self._frames_to_observe:
                """
                Create frames and calculate the time they were taken, this is done here because obtaining the time
                takes a lot of CPU time and it's not worth doing while receiving the frames from the camera. Note that
                the first frame will be the same as the last of the previous batch, so we add the previous frame so as
                to not calculate everything again, including everything needed by the observer, so the last frame
                won't be analysed by the observer until the next batch arrives and will be the first frame of that
                batch. This does not occur on the first run, in which all the frames will be analysed and the last one
                will be analysed twice, on the first run and on the second one, but will be stored only once if needed.
                """
                frames, frame_rate = self._frames_to_observe.popleft()

                if not last_time_stored:
                    last_time_stored = self._last_time_stored(frame_rate)

                frames = [Frame(frame, self._calculate_time_taken(last_time_stored, frame_rate, i+1).time())
                          for i, frame in enumerate(frames)]

                last_time_stored = self._calculate_time_taken(last_time_stored, frame_rate, len(frames))

                lf = frames[-1]

                if last_frame:
                    frames.insert(0, last_frame)

                movement = self._observer.observe(frames)

                for handler in self._motion_handlers:
                    handler.handle(movement)

                last_frame = lf

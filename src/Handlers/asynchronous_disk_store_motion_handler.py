from src.Handlers.motion_handler import MotionHandler
from collections import deque
from threading import Thread, Semaphore
import os
from src.constants import STORING_PATH
import cv2


class AsynchronousDiskStoreMotionHandler(MotionHandler):
    """
    Handles motion storing the frames on disk asynchronously.
    """
    def __init__(self, storing_path: str, seconds_to_buffer: int = 0, frame_rate: int = 0):
        """
        Initializes the handler.
        :param storing_path: Folder name to which store the frames.
        :param buffer_size: If set, the frames will be stored as soon as the buffer reaches this number of frames,
        if not set, the frames will be stored as soon as they arrive to the handler.
        """
        self._frames = deque()
        self._frame_rate = frame_rate

        if seconds_to_buffer:
            self._frames.append([])

        self._frames_ready = Semaphore(0)
        self._done = False
        self._storing_path = os.path.join(STORING_PATH, storing_path)

        if not os.path.exists(self._storing_path):
            os.mkdir(self._storing_path)

        self._buffer_size = seconds_to_buffer*frame_rate

        self._background_thread = Thread(target=self._store, args=())
        self._background_thread.start()

        super().__init__()

    def handle(self, event: list):
        """
        Receives the frames and once the handler is ready stores them.
        :param event: List of frames in which there has been movement.
        """
        if event and not self._done:
            if self._buffer_size:
                self._frames[0] = self._frames[0] + event

                if len(self._frames[0]) >= self._buffer_size:
                    self._frames.append([])
                    self._frames_ready.release()
            else:
                self._frames.append(event)
                self._frames_ready.release()

    def stop(self):
        """
        Stops the background thread running _store.
        """
        self._done = True
        self._frames_ready.release()
        self._background_thread.join()
        self._done = False

        while self._frames_ready.acquire(blocking=False):
            continue

    def _store(self):
        """
        Waits for frames to be ready and stores them on disk.
        """
        while not self._done:
            self._frames_ready.acquire()

            if self._frames:
                frames = self._frames.popleft()

                if self._buffer_size:
                    filename = "{}.mp4".format(frames[0].time)

                    self._store_video(frames, filename)
                else:
                    frames[0].store(self._storing_path)

                del frames

        while self._frames:
            frames = self._frames.popleft()

            if self._buffer_size:
                filename = "{}.mp4".format(frames[0].time)

                self._store_video(frames, filename)
            else:
                frames[0].store(self._storing_path)

            del frames

    def _store_video(self, frames, filename):
        month = frames[0].date.month if frames[0].date.month > 9 else "0{}".format(frames[0].date.month)
        day = frames[0].date.day if frames[0].date.day > 9 else "0{}".format(frames[0].date.day)
        date_str = "{}-{}-{}".format(frames[0].date.year, month, day)

        storing_path = os.path.join(self._storing_path, date_str)

        if not os.path.exists(storing_path):
            os.mkdir(storing_path)

        storing_path = os.path.join(storing_path, filename)
        height, width, layers = frames[0].frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(storing_path, fourcc, self._frame_rate, (width, height))

        for frame in frames:
            try:
                video.write(frame.frame)
            except:
                pass

        video.release()
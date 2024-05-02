from datetime import datetime
from src.cameras import Camera
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
import src.api.cameras as api
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_BUFFERSIZE, CAP_FFMPEG
from numpy import ndarray
import logging
import time

from src.handlers import FrameHandler


class LiveRetrievalStrategy(RetrievalStrategy):
    def __init__(self, camera: Camera, frames_handler: FrameHandler):
        super().__init__(camera, frames_handler)
        self._live_video = None
        self._disconnect = False

    def connect(self):
        connected = False
        i = 0
        while not connected and not self._disconnect:
            try:
                if self._live_video:
                    self._live_video.release()

                self._live_video = VideoCapture(self._camera.video_url, CAP_FFMPEG)
                self._live_video.set(CAP_PROP_FPS, self._camera.frame_rate)
                self._live_video.set(CAP_PROP_FRAME_WIDTH, self._camera.frame_width)
                self._live_video.set(CAP_PROP_FRAME_HEIGHT, self._camera.frame_height)
                self._live_video.set(CAP_PROP_BUFFERSIZE, 3)

                connected, frame = self._live_video.read()

                if not connected:
                    self._log_status(f"Connection failed")
            except Exception as e:
                self._log_status(f"Connection failed: {e}")

            if not connected and not self._disconnect:
                seconds = 2 ** i
                time.sleep(seconds)
                i = min(i + 1, 10)
        self._log_status("Connected")

    def retrieve(self) -> ndarray:
        grabbed, frame = self._live_video.read()

        while not grabbed and not self._disconnect:
            self._log_status("Lost connection to camera, reconnecting...")
            self.connect()
            grabbed, frame = self._live_video.read()

        return frame

    def disconnect(self):
        if self._live_video and not self._disconnect:
            self._log_status("Disconnected")
            self._live_video.release()

        self._disconnect = True

    def _log_status(self, status: str):
        api.log_connection_status(self._camera.id, status, datetime.now())
        message_to_log = f"Status updated for {self._camera.name} @ {self._camera.ip}:{self._camera.port}: {status}"
        logging.info(message_to_log)

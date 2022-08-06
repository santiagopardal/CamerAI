from datetime import datetime
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
import src.api.cameras as api
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_BUFFERSIZE, CAP_FFMPEG
from numpy import ndarray
from time import sleep


class LiveRetrievalStrategy(RetrievalStrategy):
    def __init__(self, camera):
        self._camera = camera
        self._live_video = None

    def connect(self):
        connected = False
        i = 0
        while not connected:
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
                    api.log_connection_status(self._camera.id, f"Connection failed", datetime.now())
            except Exception as e:
                api.log_connection_status(self._camera.id, f"Connection failed: {e}", datetime.now())

            if not connected:
                seconds = 2 ** i
                sleep(seconds)
                if i < 10:
                    i += 1

        api.log_connection_status(self._camera.id, "Connected", datetime.now())

    def retrieve(self) -> ndarray:
        grabbed, frame = self._live_video.read()

        while not grabbed:
            api.log_connection_status(self._camera.id, "Lost connection to camera, reconnecting...", datetime.now())
            self.connect()
            grabbed, frame = self._live_video.read()

        return frame

    def disconnect(self):
        if self._live_video:
            self._live_video.release()
            del self._live_video

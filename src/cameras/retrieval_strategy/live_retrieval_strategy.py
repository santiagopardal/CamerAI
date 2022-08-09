from datetime import datetime
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
import src.api.cameras as api
from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_BUFFERSIZE, CAP_FFMPEG
from numpy import ndarray
import asyncio


class LiveRetrievalStrategy(RetrievalStrategy):
    def __init__(self, camera):
        self._camera = camera
        self._live_video = None
        self._disconnect = False

    async def connect(self):
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
                await asyncio.sleep(seconds)
                if i < 10:
                    i += 1

        self._log_status("Connected")

    async def retrieve(self) -> ndarray:
        grabbed, frame = self._live_video.read()

        while not grabbed:
            self._log_status("Lost connection to camera, reconnecting...")
            await self.connect()
            grabbed, frame = self._live_video.read()

        return frame

    def disconnect(self):
        if self._live_video and not self._disconnect:
            self._log_status("Disconnected")
            self._live_video.release()
            del self._live_video

        self._disconnect = True

    def _log_status(self, status: str):
        asyncio.create_task(api.log_connection_status(self._camera.id, status, datetime.now()))

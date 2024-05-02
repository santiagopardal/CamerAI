import logging
from concurrent.futures import ThreadPoolExecutor
from numpy import ndarray
from src.cameras import Camera
from src.handlers import FrameHandler


class RetrievalStrategy:

    def __init__(self, camera: Camera):
        self._camera = camera
        self._should_receive_frames = False
        self._thread_pool = None
        self._frame_handler = FrameHandler()

    def connect(self):
        pass

    def receive_video(self):
        self._should_receive_frames = True
        self._thread_pool = ThreadPoolExecutor(max_workers=1)
        self._thread_pool.submit(self._receive_frames)

    def stop_receiving_video(self):
        self._should_receive_frames = False
        self._thread_pool.shutdown()

    def retrieve(self) -> ndarray:
        pass

    def disconnect(self):
        pass

    def _receive_frames(self):
        self.connect()

        while self._should_receive_frames:
            try:
                frame = self.retrieve()
                self._camera.last_frame = frame
                self._camera.frame_handler.handle(frame)
            except Exception as e:
                logging.error(
                    f"Error downloading image from camera {self._camera.name} @ "
                    f"{self._camera.ip}:{self._camera.port}: {e}"
                )

        self.disconnect()
        self._camera.frame_handler.stop()

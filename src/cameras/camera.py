import asyncio
from src.handlers import FrameHandler
from src.handlers import BufferedMotionHandler
from src.observations import DontLookBackObserver
from concurrent.futures import ThreadPoolExecutor
from src.constants import SECONDS_TO_BUFFER
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from numpy import ndarray
import src.observations.models.factory as model_factory
import logging


class Camera:
    def __init__(self, id: int, ip: str, port: int, video_url: str, snapshot_url: str, name: str, frame_rate: int, frame_width: int,
                 frame_height: int, sensitivity: int, retrieval_strategy: RetrievalStrategy = None, frames_handler: FrameHandler = None):
        self._id = id
        self._ip = ip
        self._port = port
        self._video_url = video_url
        self._snapshot_url = snapshot_url
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._name = name
        self._frame_rate = frame_rate
        self._should_receive_frames = False
        self._last_frame = None
        self._frame_handler = FrameHandler() if frames_handler is None else frames_handler
        self._retrieval_strategy = retrieval_strategy
        self._is_recording = False
        self._sensitivity = sensitivity
        self._thread_pool = ThreadPoolExecutor(max_workers=1)

    @classmethod
    def from_json(cls, json: dict):
        pass

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def video_url(self) -> str:
        return self._video_url

    @property
    def snapshot_url(self) -> str:
        return self._snapshot_url

    @property
    def frame_rate(self) -> int:
        return self._frame_rate

    @property
    def frame_width(self) -> int:
        return self._frame_width

    @property
    def frame_height(self) -> int:
        return self._frame_width

    @property
    def frame_handler(self) -> FrameHandler:
        return self._frame_handler

    @property
    def retrieval_strategy(self) -> RetrievalStrategy:
        return self._retrieval_strategy

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @ip.setter
    def ip(self, ip: str):
        self._ip = ip

    @port.setter
    def port(self, port: int):
        self._port = port

    @frame_handler.setter
    def frame_handler(self, frames_handler: FrameHandler):
        self._frame_handler.stop()
        self._frame_handler = frames_handler
        self._frame_handler.start()

    @retrieval_strategy.setter
    def retrieval_strategy(self, retrieval_strategy: RetrievalStrategy):
        self._retrieval_strategy = retrieval_strategy

    def screenshot(self) -> ndarray:
        return self._last_frame

    def receive_video(self):
        self._should_receive_frames = True
        self._thread_pool.submit(self._receive_frames)

    def record(self):
        if not self.is_recording:
            self._frame_handler.set_observer(DontLookBackObserver(model_factory, self._sensitivity))
            self._frame_handler.add_motion_handler(BufferedMotionHandler(self, SECONDS_TO_BUFFER))
            self._frame_handler.start()
            self._is_recording = True

    def stop_recording(self):
        if self.is_recording:
            self._frame_handler.stop()
            self._frame_handler.set_motion_handlers([])
            self._is_recording = False

    def stop_receiving_video(self):
        self._should_receive_frames = False
        self.retrieval_strategy.disconnect()
        self._thread_pool.shutdown(True)

    def _receive_frames(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._retrieval_strategy.connect())

        while self._should_receive_frames:
            try:
                frame = loop.run_until_complete(self._retrieval_strategy.retrieve())
                self._last_frame = frame
                loop.create_task(self._frame_handler.handle(frame))
            except Exception as e:
                logging.error(f"Error downloading image from camera {self._name} @ {self._ip}:{self._port}: {e}")

        loop.run_until_complete(self._retrieval_strategy.disconnect())
        self._frame_handler.stop()
        loop.close()

    def __hash__(self):
        return "{}:{}@{}".format(self.ip, self.port, self.name).__hash__()

    def __eq__(self, other):
        return isinstance(other, Camera) and other.ip == self._ip and other.port == self._port

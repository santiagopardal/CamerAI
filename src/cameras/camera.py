from src.handlers import FrameHandler
from src.handlers import BufferedMotionHandler
from src.observations import DontLookBackObserver
from concurrent.futures import ThreadPoolExecutor
from src.constants import SECONDS_TO_BUFFER
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from numpy import ndarray
import src.observations.models.factory as model_factory
from src.cameras.properties import Properties
from src.cameras.configurations import Configurations
import logging


class Camera:
    def __init__(self, properties: Properties, configurations: Configurations, video_url: str, snapshot_url: str, retrieval_strategy: RetrievalStrategy = None, frames_handler: FrameHandler = None):
        self._properties = properties
        self._configurations = configurations
        self._video_url = video_url
        self._snapshot_url = snapshot_url
        self._should_receive_frames = False
        self._last_frame = None
        self._frame_handler = FrameHandler() if frames_handler is None else frames_handler
        self._retrieval_strategy = retrieval_strategy
        self._thread_pool = ThreadPoolExecutor(max_workers=1)
        if self.is_recording:
            self._do_record()

    @property
    def id(self) -> int:
        return self._properties.id

    @property
    def name(self) -> str:
        return self._properties.name

    @property
    def ip(self) -> str:
        return self._properties.ip

    @property
    def port(self) -> int:
        return self._properties.port

    @property
    def video_url(self) -> str:
        return self._video_url

    @property
    def snapshot_url(self) -> str:
        return self._snapshot_url

    @property
    def frame_rate(self) -> int:
        return self._properties.frame_rate

    @property
    def frame_width(self) -> int:
        return self._properties.frame_width

    @property
    def frame_height(self) -> int:
        return self._properties.frame_width

    @property
    def frame_handler(self) -> FrameHandler:
        return self._frame_handler

    @property
    def retrieval_strategy(self) -> RetrievalStrategy:
        return self._retrieval_strategy

    @property
    def is_recording(self) -> bool:
        return self._configurations.recording

    @ip.setter
    def ip(self, ip: str):
        self._properties.ip = ip

    @port.setter
    def port(self, port: int):
        self._properties.port = port

    @frame_handler.setter
    def frame_handler(self, frames_handler: FrameHandler):
        self._frame_handler.stop()
        self._frame_handler = frames_handler
        self._frame_handler.start()

    @retrieval_strategy.setter
    def retrieval_strategy(self, retrieval_strategy: RetrievalStrategy):
        self._retrieval_strategy = retrieval_strategy

    def update_sensitivity(self, sensitivity: float):
        old_sensitivity = self._frame_handler.observer.sensitivity
        self._frame_handler.observer.sensitivity = sensitivity
        logging.info(f"Updated sensitivity to camera with ID {self.id} from {old_sensitivity} to {sensitivity}")

    def screenshot(self) -> ndarray:
        return self._last_frame

    def receive_video(self):
        self._should_receive_frames = True
        self._thread_pool.submit(self._receive_frames)

    def record(self):
        if not self.is_recording:
            self._do_record()

    def stop_recording(self):
        if self.is_recording:
            self._configurations.recording = False
            self._frame_handler.stop()
            self._frame_handler.set_motion_handlers([])

    def stop_receiving_video(self):
        self._should_receive_frames = False

    def _receive_frames(self):
        self._retrieval_strategy.connect()

        while self._should_receive_frames:
            try:
                frame = self._retrieval_strategy.retrieve()
                self._last_frame = frame
                self._frame_handler.handle(frame)
            except Exception as e:
                logging.error(f"Error downloading image from camera {self.name} @ {self.ip}:{self.port}: {e}")

        self._retrieval_strategy.disconnect()
        self._frame_handler.stop()

    def _do_record(self):
        self._frame_handler.observer = DontLookBackObserver(model_factory, self._configurations.sensitivity)
        self._frame_handler.add_motion_handler(BufferedMotionHandler(self, SECONDS_TO_BUFFER))
        self._frame_handler.start()
        self._configurations.recording = True

    def __hash__(self):
        return "{}:{}@{}".format(self.ip, self.port, self.name).__hash__()

    def __eq__(self, other):
        return isinstance(other, Camera) and other.ip == self.ip and other.port == self.port

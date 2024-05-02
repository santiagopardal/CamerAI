from src.handlers import FrameHandler
from src.handlers import BufferedMotionHandler
from src.observations import DontLookBackObserver
from src.constants import SECONDS_TO_BUFFER
from numpy import ndarray
import src.observations.models.factory as model_factory
from src.cameras.properties import Properties
from src.cameras.configurations import Configurations
import logging


class Camera:
    def __init__(self, properties: Properties, configurations: Configurations, video_url: str, snapshot_url: str, frames_handler: FrameHandler = None):
        self._properties = properties
        self._configurations = configurations
        self._video_url = video_url
        self._snapshot_url = snapshot_url
        self._should_receive_frames = False
        self._last_frame = None
        self._frame_handler = frames_handler or FrameHandler()
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
    def is_recording(self) -> bool:
        return self._configurations.recording

    @property
    def configurations(self) -> Configurations:
        return self._configurations

    @property
    def last_frame(self) -> ndarray:
        return self._last_frame

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

    @last_frame.setter
    def last_frame(self, last_frame: ndarray):
        self._last_frame = last_frame

    def update_sensitivity(self, sensitivity: float):
        old_sensitivity = self._frame_handler.observer.sensitivity
        self._frame_handler.observer.sensitivity = sensitivity
        logging.info(f"Updated sensitivity to camera with ID {self.id} from {old_sensitivity} to {sensitivity}")

    def screenshot(self) -> ndarray:
        return self._last_frame

    def record(self):
        if not self.is_recording:
            self._do_record()

    def stop_recording(self):
        if self.is_recording:
            self._configurations.recording = False
            self._frame_handler.stop()

    def _do_record(self):
        self._frame_handler.observer = DontLookBackObserver(model_factory, self._configurations.sensitivity)
        self._frame_handler.add_motion_handler(BufferedMotionHandler(self, SECONDS_TO_BUFFER))
        self._frame_handler.start()
        self._configurations.recording = True

    def __hash__(self):
        return hash(f"{self.ip}:{self.port}@{self.name}")

    def __eq__(self, other):
        return isinstance(other, Camera) and other.ip == self.ip and other.port == self.port

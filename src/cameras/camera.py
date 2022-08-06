from src.handlers.frame_handler import FrameHandler
from src.handlers.buffered_motion_handler import BufferedMotionHandler
from src.observations.observers.observer import Observer
from concurrent.futures import ThreadPoolExecutor
from src.constants import SECONDS_TO_BUFFER
from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
from numpy import ndarray
import src.observations.models.factory as model_factory


class Camera:

    _retrieval_strategy: RetrievalStrategy
    _id: int
    _ip: str
    _port: int
    _video_url: str
    _name: str
    _frame_rate: int
    _frame_width: int
    _frame_height: int
    _kill_thread: bool
    _last_frame: ndarray
    _frame_handler: FrameHandler
    _thread_pool: ThreadPoolExecutor

    def __init__(self, id: int, ip: str, port: int, video_url: str, name: str, frame_rate: int, frame_width: int,
                 frame_height: int, retrieval_strategy: RetrievalStrategy = None, frames_handler: FrameHandler = None):
        """
        :param ip: IP of the camera.
        :param port: Port for the camera's IP.
        :param name: name where the camera is located, this will be the name of the folder where the frames will
        be stored.
        :param frame_rate: Camera's frame rate.
        :param frames_handler: Handler to handle new frames.
        """
        self._id = id
        self._ip = ip
        self._port = port
        self._video_url = video_url
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._name = name
        self._frame_rate = frame_rate
        self._kill_thread = False
        self._last_frame = None
        self._frame_handler = FrameHandler() if frames_handler is None else frames_handler
        self._retrieval_strategy = retrieval_strategy
        self._thread_pool = ThreadPoolExecutor(max_workers=1)

    @classmethod
    def from_json(cls, json: dict):
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into camera.
        :return: Camera from the dictionary.
        """
        return cls(
            json["id"], json["ip"], json["http_port"],
            json["name"], json["frame_rate"], json["retrieval_strategy"]
        )

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

    @ip.setter
    def ip(self, ip: str):
        self._ip = ip

    @port.setter
    def port(self, port: int):
        self._port = port

    @frame_handler.setter
    def frame_handler(self, frames_handler: FrameHandler):
        """
        Changes the frames handler.
        :param frames_handler: New frames handler.
        """
        self._frame_handler.stop()
        self._frame_handler = frames_handler
        self._frame_handler.start()

    @retrieval_strategy.setter
    def retrieval_strategy(self, retrieval_strategy: RetrievalStrategy):
        self._retrieval_strategy = retrieval_strategy

    def screenshot(self) -> ndarray:
        """
        :return: A screenshot from the camera.
        """
        return self._last_frame

    def receive_video(self):
        """
        Starts thread to receive video.
        """
        self._thread_pool.submit(self._receive_frames)

    def record(self):
        """
        Starts recording.
        """
        self._frame_handler.set_observer(Observer(model_factory))
        self._frame_handler.add_motion_handler(BufferedMotionHandler(self, SECONDS_TO_BUFFER))
        self._frame_handler.start()

    def stop_recording(self):
        """
        Stops recording.
        """
        self._frame_handler.stop()
        self._frame_handler.set_motion_handlers([])

    def stop_receiving_video(self):
        """
        Stops receiving video.
        """
        self._kill_thread = True

    def _receive_frames(self):
        """
        Obtains live images from the camera and calls the frames handler to handle them.
        """
        self._retrieval_strategy.connect()

        while not self._kill_thread:
            try:
                frame = self._retrieval_strategy.retrieve()

                self._last_frame = frame
                self._frame_handler.handle(frame)
            except Exception as e:
                print("Error downloading image from camera {} on ip {}".format(self._name, self._ip))
                print(e)

        self._retrieval_strategy.disconnect()
        self._frame_handler.stop()
        self._kill_thread = False

    def __hash__(self):
        return "{}:{}@{}".format(self.ip, self.port, self.name).__hash__()

    def __eq__(self, other):
        return isinstance(other, Camera) and other.ip == self._ip and other.port == self._port

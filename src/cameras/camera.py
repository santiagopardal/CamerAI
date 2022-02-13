import time
import cv2
import numpy as np
import requests
from src.handlers.frame_handler import FrameHandler
from src.handlers.buffered_motion_handler import BufferedMotionHandler
from src.observations.observers.observer import Observer
from src.observations.observers.dynamic_movement_detection_observer import DynamicMovementDetectionObserver
from concurrent.futures import ThreadPoolExecutor
from src.constants import SECONDS_TO_BUFFER, FRAME_RATE


class Camera:
    def __init__(self, id: int, ip: str, port: int, place: str, screenshot_url: str, frame_rate: int,
                 frames_handler: FrameHandler = None):
        """
        :param ip: IP of the camera.
        :param port: Port for the camera's IP.
        :param place: Place where the camera is located, this will be the name of the folder where the frames will
        be stored.
        :param screenshot_url: URL to obtain screenshot from the CCTV camera.
        :param frame_rate: Camera's frame rate.
        :param frames_handler: Handler to handle new frames.
        """

        super().__init__()
        self._id = id
        self._ip = ip
        self._port = port
        self._place = place
        self._screenshot_url = screenshot_url
        self._frame_rate = frame_rate
        self._record_thread = None
        self._kill_thread = False
        self._last_frame = None
        self._frames_handler = FrameHandler() if frames_handler is None else frames_handler
        self._thread_pool = ThreadPoolExecutor(max_workers=2)

    @classmethod
    def from_json(cls, json: dict):
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into camera.
        :return: Camera from the dictionary.
        """
        pass

    @property
    def id(self) -> int:
        return self._id

    @property
    def place(self) -> str:
        return self._place

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def last_frame(self) -> np.ndarray:
        return self._last_frame

    @property
    def frame_rate(self) -> int:
        return self._frame_rate

    @ip.setter
    def ip(self, ip: str):
        self._ip = ip

    @port.setter
    def port(self, port: int):
        self._port = port

    def set_frames_handler(self, frames_handler: FrameHandler):
        """
        Changes the frames handler.
        :param frames_handler: New frames handler.
        """
        self._frames_handler.stop()
        self._frames_handler = frames_handler
        self._frames_handler.start()

    def screenshot(self):
        """
        :return: A screenshot from the camera.
        """
        response = requests.get(self._screenshot_url, stream=True).raw
        frame = np.asarray(bytearray(response.read()), dtype="uint8")

        return cv2.imdecode(frame, cv2.IMREAD_COLOR)

    def receive_video(self):
        """
        Starts thread to receive video.
        """
        self._prepare_connection()
        self._thread_pool.submit(self._receive_frames)

    def _prepare_connection(self):
        """
        Prepares the connection to receive frames from camera
        """
        pass

    def record(self):
        """
        Starts recording.
        """
        self._frames_handler.set_observer(DynamicMovementDetectionObserver())
        self._frames_handler.add_motion_handler(BufferedMotionHandler(self, SECONDS_TO_BUFFER))
        self._frames_handler.start()

    def stop_recording(self):
        """
        Stops recording.
        """
        self._frames_handler.stop()
        self._frames_handler.set_observer(Observer())
        self._frames_handler.set_motion_handlers([])

    def stop_receiving_video(self):
        """
        Stops receiving video.
        """
        if self._record_thread:
            self._kill_thread = True
            self._record_thread.join()
            self._record_thread = None
            self._kill_thread = False

        self._frames_handler.stop()

    def _receive_frames(self):
        """
        Obtains live images from the camera and calls the frames handler to handle them.
        """
        previous_capture = 0

        while not self._kill_thread:
            if time.perf_counter() - previous_capture >= 1 / FRAME_RATE:

                try:
                    previous_capture = time.perf_counter()

                    frame = self.screenshot()

                    if frame:
                        self._last_frame = frame
                        self._frames_handler.handle(frame)

                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self._place, self._ip))
                    print(e)

    def __hash__(self):
        return "{}:{}@{}".format(self.ip, self.port, self.place).__hash__()

    def __eq__(self, other):
        if isinstance(other, Camera):
            return other.ip == self._ip and other.port == self._port

        return False

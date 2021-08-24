import urllib
import io
import time
import cv2
import constants
import numpy as np
import requests
from PIL import Image
from Handlers.frame_handler import FrameHandler
from Handlers.asynchronous_disk_store_motion_handler import AsynchronousDiskStoreMotionHandler
from Observations.Observers.observer import Observer
from Observations.Observers.lite_observer import LiteObserver
from concurrent.futures import ThreadPoolExecutor
from Observer.observer import Publisher


class Camera(Publisher):
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str, framerate: int,
                 frames_handler: FrameHandler = None):
        """
        :param ip: IP of the camera.
        :param port: Port for the camera's IP.
        :param place: Place where the camera is located, this will be the name of the folder where the frames will
        be stored.
        :param screenshot_url: URL to obtain screenshot from the CCTV camera.
        :param framerate: Camera's framerate.
        :param frames_handler: Handler to handle new frames.
        """

        super().__init__()
        self._ip = ip
        self._port = port
        self._place = place
        self._screenshot_url = screenshot_url
        self._framerate = framerate
        self._record_thread = None
        self._kill_thread = False
        self._last_frame = None
        self._frames_handler = FrameHandler() if frames_handler is None else frames_handler
        self._thread_pool = ThreadPoolExecutor(max_workers=2)

    @classmethod
    def from_dict(cls, json: dict):
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into camera.
        :return: Camera from the dictionary.
        """
        pass

    def to_dict(self) -> dict:
        """
        Transforms a camera into a dictionary for serialization.
        :return: dictionary representing the camera.
        """
        pass

    def _to_pop_from_dict(self) -> list:
        """
        Returns list of attributes to remove when transforming camera to dictionary.
        :return: list of attributes to remove.
        """
        return ["_record_thread", "_kill_thread", "_last_frame", "_subscriptors", "_frames_handler"]

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
    def framerate(self) -> int:
        return self._framerate

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

    def screenshot(self) -> Image.Image:
        """
        :return: A screenshot from the camera.
        """
        with urllib.request.urlopen(self._screenshot_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def receive_video(self):
        """
        Starts thread to receive video.
        """
        self._thread_pool.submit(self._receive_video)

    def _receive_video(self):
        """
        Tries to get video.
        """
        self._thread_pool.submit(self._receive_frames)

    def record(self):
        """
        Starts recording.
        """
        self._frames_handler.set_observer(LiteObserver())
        self._frames_handler.add_motion_handler(AsynchronousDiskStoreMotionHandler(self._place))
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

    def _acquire_frame(self):
        response = requests.get(self._screenshot_url, stream=True).raw
        frame = np.asarray(bytearray(response.read()), dtype="uint8")

        return cv2.imdecode(frame, cv2.IMREAD_COLOR)

    def _receive_frames(self):
        """
        Obtains live images from the camera, notifies subscribers and calls the frames handler to handle them.
        """
        previous_capture = 0

        while not self._kill_thread:
            if time.perf_counter() - previous_capture >= 1 / constants.FRAMERATE:

                try:
                    previous_capture = time.perf_counter()

                    frame = self._acquire_frame()

                    if frame:
                        self._last_frame = frame
                        self._notify_subscribed()
                        self._frames_handler.handle(frame)

                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self._place, self._ip))
                    print(e)

    def __hash__(self):
        return (self.ip + str(self._port) + self._place).__hash__()

    def __eq__(self, other):
        if isinstance(other, Camera):
            return other.ip == self._ip and other.port == self._port

        return False


class LiveVideoCamera(Camera):
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str,
                 live_video_url: str, width: int, height: int,
                 framerate: int, frames_handler: FrameHandler = None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located, this will be the folder's name where the frames will be stored.
        :param screenshot_url: Screenshot URL for camera.
        :param live_video_url: Live video URL for camera.
        :param width: Width of frame.
        :param height: Height of frame.
        """
        super().__init__(ip, port, place, screenshot_url, framerate, frames_handler)

        self._live_video_url = live_video_url
        self._live_video = None
        self._frame_width = width
        self._frame_height = height

    def _to_pop_from_dict(self) -> list:
        """
        Returns list of attributes to remove when transforming camera to dictionary.
        :return: List of attributes to remove.
        """
        res = super()._to_pop_from_dict()
        res.append("_live_video")
        return res

    def _receive_video(self):
        """
        Tries to receive video.
        """
        while (not self._live_video) or (not self._live_video.isOpened()):      # While not connected or video is not
            self.__connect()                                                    # opened, connect!

        if self._record_thread:                                                 # If there was another thread running
            self._kill_thread = True                                            # stop it,
            self._record_thread.join()                                          # wait for it to finish
            self._kill_thread = False                                           # reset variables.

        super()._receive_video()

    def stop_receiving_video(self):
        """
        Stops receiving video from the camera.
        """
        super().stop_receiving_video()

        self._live_video.release()

    def _acquire_frame(self):
        grabbed, frame = self._live_video.read()

        while not grabbed:
            print("Reconnecting!")
            self.__connect()
            self._acquire_frame()

        return frame

    def _receive_frames(self):
        """
        Obtains live images from the camera, notifies subscribers and calls the frames handler to handle them.
        """

        while not self._kill_thread:
            try:
                frame = self._acquire_frame()

                self._last_frame = frame
                self._notify_subscribed()
                self._frames_handler.handle(frame)
            except Exception as e:
                print("Error downloading image from camera {} on ip {}".format(self._place, self._ip))
                print(e)
                self.__connect()

        self._frames_handler.stop()

    def __connect(self):
        """
        Connects to the camera.
        """
        connected = False
        i = 0
        while not connected:
            try:
                if self._live_video:
                    print("Reconnecting camera at {} on IP {}".format(self._place, self._ip))
                    self._live_video.release()
                    del self._live_video

                self._live_video = cv2.VideoCapture(self._live_video_url, cv2.CAP_FFMPEG)
                self._live_video.set(cv2.CAP_PROP_FPS, self._framerate)
                self._live_video.set(cv2.CAP_PROP_FRAME_WIDTH, self._frame_width)
                self._live_video.set(cv2.CAP_PROP_FRAME_HEIGHT, self._frame_height)
                self._live_video.set(cv2.CAP_PROP_BUFFERSIZE, 3)

                connected = True

                print("Connected camera at {} on IP {}".format(self._place, self._ip))
            except Exception as e:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print(e)
                print("Could not connect, retrying in {} seconds".format(seconds))
                time.sleep(seconds)

    def __eq__(self, other):
        if isinstance(other, LiveVideoCamera):
            return super().__eq__(other)

        return False


class FI9803PV3(LiveVideoCamera):
    def __init__(self, ip: str, port: int, streaming_port: int,
                 place: str, user: str, password: str,
                 frames_handler: FrameHandler = None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param streaming_port: Port to receive live video.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        screenshot_url = "http://{}:{}/{}".format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}")
        screenshot_url = screenshot_url.format(user, password)

        live_video_url = "{}@{}:{}/videoMain".format("rtsp://{}:{}", ip, str(streaming_port))
        live_video_url = live_video_url.format(user, password)

        super().__init__(ip, port, place,
                         screenshot_url, live_video_url,
                         1280, 720, 23, frames_handler)

        self._streaming_port = streaming_port

    def to_dict(self) -> dict:
        """
        Transforms a camera into a dictionary for serialization.
        :return: dictionary representing the camera.
        """
        res = self.__dict__.copy()

        for key in self._to_pop_from_dict():
            res.pop(key)

        res["model"] = "FI9803PV3"

        return res

    @classmethod
    def from_dict(cls, json: dict) -> Camera:
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into FI9803PV3 camera.
        :return: FI9803PV3 camera from the dictionary.
        """
        return cls(json["_ip"], json["_port"], json["_streaming_port"],
                   json["_place"], json["_user"], json["_password"])

    def __eq__(self, other):
        if isinstance(other, FI9803PV3):
            return super().__eq__(other)

        return False


class FI89182(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str,
                 user: str, password: str,
                 frames_handler: FrameHandler = None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        screenshot_url = "http://{}:{}/{}".format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}")
        screenshot_url = screenshot_url.format(user, password)

        live_video_url = "http://{}:{}/{}".format(ip, port, "videostream.cgi?user={}&pwd={}")
        live_video_url = live_video_url.format(user, password)

        super().__init__(ip, port, place,
                         screenshot_url, live_video_url,
                         640, 480, 15, frames_handler)

    def to_dict(self) -> dict:
        """
        Transforms a camera into a dictionary for serialization.
        :return: dictionary representing the camera.
        """
        res = self.__dict__.copy()

        for key in self._to_pop_from_dict():
            res.pop(key)

        res["model"] = "FI89182"

        return res

    @classmethod
    def from_dict(cls, json: dict) -> Camera:
        """
        Returns a Camera from a dictionary.
        :param json: Dictionary to transform into FI89182 camera.
        :return: FI89182 camera from the dictionary.
        """
        return cls(json["_ip"], json["_port"], json["_place"], json["_user"], json["_password"])

    def __eq__(self, other):
        if isinstance(other, FI89182):
            return super().__eq__(other)

        return False

import urllib
import io
import time
import cv2
import threading
import Constants
import numpy as np
import requests
from PIL import Image
from Handlers.Handler import MotionDetectorFrameHandler, FrameHandler


class Subscriber:
    def notify(self):
        pass


class Camera:
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str, framerate: int, frames_handler=None):
        """
        :param ip: IP of the camera.
        :param port: Port for the camera live stream.
        :param place: Place where the camera is located, this will be the name of the folder where the frames will
        be stored.
        :param screenshot_url: URL to obtain screenshot from the CCTV camera.
        :param framerate: Camera's framerate.
        :param frames_handler: Handler to handle new frames.
        """

        self._ip = ip
        self._port = port
        self._place = place
        self._screenshot_url = screenshot_url
        self._framerate = framerate
        self._record_thread = None
        self._kill_thread = False
        self._last_frame = None
        self._subscriptors = []
        self._frames_handler = MotionDetectorFrameHandler(self) if frames_handler is None else frames_handler

    def _to_pop_from_dict(self):
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

    def subscribe(self, sub: Subscriber):
        """
        Adds a new subscriber to the list.
        :param sub: Subscriber to add.
        """
        self._subscriptors.append(sub)

    def unsubscribe(self, sub: Subscriber):
        """
        Unsubscribes a subscriber if already subscribed.
        :param sub: Subscriber.
        """
        if sub in self._subscriptors:
            self._subscriptors.remove(sub)

    def _notify_subscribed(self):
        """
        Notifies all subscribed that a new frame is ready to be read.
        """
        for sub in self._subscriptors:
            sub.notify()

    def set_frames_handler(self, frames_handler: FrameHandler):
        """
        Changes the frames handler.
        :param frames_handler: New frames handler.
        """
        self._frames_handler.stop()
        self._frames_handler = frames_handler
        self._frames_handler.start()

    def __eq__(self, other):
        if isinstance(other, Camera):
            return other.ip == self._ip and other.port == self._port

        return False

    def screenshot(self):
        """
        :return: A screenshot from the camera.
        """
        with urllib.request.urlopen(self._screenshot_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def receive_video(self):
        """
        Starts obtaining video.
        """
        self._record_thread = threading.Thread(target=self._receive_frames)
        self._record_thread.start()

    def start_recording(self):
        """
        Starts recording, this changes the frames handler.
        """
        self._frames_handler.stop()
        self._frames_handler = MotionDetectorFrameHandler(self)
        self._frames_handler.start()

    def stop_recording(self):
        """
        Stops recording, this changes the frames handler.
        """
        self._frames_handler.stop()
        self._frames_handler = FrameHandler(self)
        self._frames_handler.start()

    def stop_receiving_video(self):
        """
        Stops receiving video.
        """
        if self._record_thread is not None:
            self._kill_thread = True
            self._record_thread.join()
            self._record_thread = None
            self._kill_thread = False

        self._frames_handler.stop()

    def _receive_frames(self):
        """
        Obtains live images from the camera and tells the frames handler to handle them.
        """
        previous_capture = 0
        self._frames_handler.start()

        while not self._kill_thread:
            if time.perf_counter() - previous_capture >= 1 / Constants.FRAMERATE:

                try:
                    previous_capture = time.perf_counter()

                    response = requests.get(self._screenshot_url, stream=True).raw

                    frame = np.asarray(bytearray(response.read()), dtype="uint8")
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                    if frame is not None:
                        self._last_frame = frame
                        self._notify_subscribed()
                        self._frames_handler.handle(frame)

                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self._place, self._ip))
                    print(e)

        self._frames_handler.stop()

    def __hash__(self):
        return self._place.__hash__()


class LiveVideoCamera(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str,
                 screenshot_url: str, live_video_url: str, width: int, height: int, frames_handler=None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located, this will be the folder's name where the frames will be stored.
        :param user: Username to connect to camera.
        :param password: Password for username.
        :param screenshot_url: Screenshot URL for camera.
        :param live_video_url: Live video URL for camera.
        :param width: Width of frame.
        :param height: Height of frame.
        """
        self._user = user
        self._password = password

        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        super().__init__(ip, port, place, screenshot_url.format(user, password), Constants.FRAMERATE, frames_handler)

        self._live_video_url = live_video_url.format(user, password)
        self._live_video = None
        self._frame_width = width
        self._frame_height = height
        self.__connect()

    def _to_pop_from_dict(self):
        res = super()._to_pop_from_dict()
        res.append("_live_video")
        return res

    def receive_video(self):
        """
        Starts obtaining video.
        """
        try:
            while self._live_video is None or not self._live_video.isOpened():
                self.__connect()

            self.__initialize_record_thread()
        except Exception as e:
            while not self._live_video.isOpened():
                print("Error downloading image from camera {} on ip {}".format(self._place, self._ip))
                print(e)
                self.__connect()

    def __initialize_record_thread(self):
        """
        Initializes the recording thread.
        """
        if self._record_thread is not None:
            self._kill_thread = True
            self._record_thread.join()
            self._kill_thread = False

        self._record_thread = threading.Thread(target=self._receive_frames)
        self._record_thread.start()

    def _receive_frames(self):
        """
        Obtains live images from the camera and tells the frames handler to handle them.
        """
        self._frames_handler.start()

        while not self._kill_thread:
            try:
                grabbed, frame = self._live_video.read()                # Read frame

                while not grabbed:                                      # If could not read frame
                    print("Reconnecting!")
                    self.__connect()                                    # Reconnect
                    grabbed, frame = self._live_video.read()            # Read again, if could not read again retry!

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
                if self._live_video is not None:
                    print("Reconnecting camera at {} on IP {}".format(self._place, self._ip))
                    self._live_video.release()
                    del self._live_video

                self._live_video = cv2.VideoCapture(self._live_video_url, cv2.CAP_FFMPEG)
                self._live_video.set(cv2.CAP_PROP_FPS, Constants.FRAMERATE)
                self._live_video.set(cv2.CAP_PROP_FRAME_WIDTH, self._frame_width)
                self._live_video.set(cv2.CAP_PROP_FRAME_HEIGHT, self._frame_height)
                self._live_video.set(cv2.CAP_PROP_BUFFERSIZE, 3)

                connected = True

                print("Connected camera at {} on IP {}".format(self._place, self._ip))
            except:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not connect, retrying in {} seconds".format(seconds))
                time.sleep(seconds)


class FI9803PV3(LiveVideoCamera):
    def __init__(self, ip: str, port: int, streaming_port: int, place: str, user: str, password: str, frames_handler=None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param streaming_port: Port to receive live video.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        super().__init__(ip, port, place, user, password, "http://{}:{}/{}".
                         format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"),
                         "{}@{}:{}/videoMain".format("rtsp://{}:{}", ip, str(streaming_port)),
                         1280, 720, frames_handler)

        self._streaming_port = streaming_port

    def to_dict(self) -> dict:
        res = self.__dict__.copy()

        for key in self._to_pop_from_dict():
            res.pop(key)

        res["model"] = "FI9803PV3"

        return res

    @staticmethod
    def from_dict(json: dict):
        return FI9803PV3(json["_ip"], json["_port"], json["_streaming_port"],
                         json["_place"], json["_user"], json["_password"])


class FI89182(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str, frames_handler=None):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        :param frames_handler: Handler to handle new frames, if set to None will use default.
        """
        super().__init__(ip, port, place, user, password,
                         "http://{}:{}/{}".
                         format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"),
                         "http://{}:{}/{}".
                         format(ip, port, "videostream.cgi?user={}&pwd={}"),
                         640, 480, frames_handler)

    def to_dict(self) -> dict:
        res = self.__dict__.copy()

        for key in self._to_pop_from_dict():
            res.pop(key)

        res["model"] = "FI89182"

        return res

    @staticmethod
    def from_dict(json: dict):
        return FI89182(json["_ip"], json["_port"], json["_place"], json["_user"], json["_password"])


class CameraDeserializator:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)

        return cls.instance

    def __init__(self):
        self._classes = {
            "FI89182": FI89182,
            "FI9803PV3": FI9803PV3
        }

    def deserialize(self, cam: dict) -> Camera:
        model = self._classes[cam["model"]]

        return model.from_dict(cam)
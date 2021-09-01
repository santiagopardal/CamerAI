import urllib
from src.Handlers.frame_handler import FrameHandler
from src.CameraUtils.Camera.live_video_camera import LiveVideoCamera
from src.CameraUtils.Camera.camera import Camera


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

        super().__init__(ip, port, place, screenshot_url, live_video_url, 1280, 720, 23, frames_handler)

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

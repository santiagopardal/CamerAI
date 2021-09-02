import time
import cv2
from src.Handlers.frame_handler import FrameHandler
from src.CameraUtils.Camera.camera import Camera


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

    def _prepare_connection(self):
        while (not self._live_video) or (not self._live_video.isOpened()):
            self.__connect()

        if self._record_thread:
            self._kill_thread = True
            self._record_thread.join()
            self._kill_thread = False

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
            grabbed, frame = self._live_video.read()

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

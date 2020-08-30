import urllib.request
import io
import time
import cv2
import threading
import Constants
import numpy as np
import requests
from PIL import Image
from MotionEventHandler import MotionEventHandler
from Frame import Frame
from Observers import Observer


class Camera:
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str):
        self._IP = ip
        self._port = port
        self._place = place
        self._screenshot_url = screenshot_url
        self._record_thread = None
        self._kill_thread = False
        self._motion_handler = MotionEventHandler()
        self._observer = Observer(self)

    def get_place(self) -> str:
        return self._place

    def set_observer(self, observer: Observer):
        self._observer = observer

    def handle_motion(self, frame: Frame):
        self._motion_handler.handle(frame)

    def set_motion_handler(self, motion_handler: MotionEventHandler):
        self._motion_handler = motion_handler

    def equals(self, cam) -> bool:
        return cam.getIP() == self._IP and cam.getPort() == self._port

    def screenshot(self):
        with urllib.request.urlopen(self._screenshot_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def record(self):
        thread = threading.Thread(target=self._record_thread_worker)
        thread.daemon = False
        thread.start()
        self._record_thread = thread

    def stop_recording(self):
        self._kill_thread = True
        self._record_thread = None

    def _record_thread_worker(self):
        previous_capture = 0
        frames = []

        while not self._kill_thread:
            if time.perf_counter() - previous_capture > 1 / Constants.FRAMERATE:

                try:
                    previous_capture = time.perf_counter()

                    response = requests.get(self._screenshot_url, stream=True).raw

                    frame = np.asarray(bytearray(response.read()), dtype="uint8")
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                    frame = Frame(frame)

                    if frame is not None:
                        frames.append(frame)
                        if len(frames) >= Constants.DBS:
                            thread = threading.Thread(target=self._observer.observe, args=(frames,))
                            thread.start()

                            frames = [frame]

                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self._place, self._IP))
                    print(e)


class LiveVideoCamera(Camera):
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str, live_video_url: str):
        super().__init__(ip, port, place, screenshot_url)

        self._live_video_url = live_video_url
        self._live_video = None
        self.__connect()

    def record(self):
        try:
            if self._live_video is not None:
                if self._live_video.isOpened():
                    self.__initialize_record_thread()
                else:
                    self.__connect()
                    self.__initialize_record_thread()
            else:
                self.__connect()
                self.__initialize_record_thread()
        except Exception as e:
            while not self._live_video.isOpened():
                print("Error downloading image from camera {} on ip {}".format(self._place, self._IP))
                print(e)
                self.__connect()

    def __initialize_record_thread(self):
        if self._record_thread is not None:
            self._kill_thread = True
            self._record_thread.join()
            self._kill_thread = False
            thread = threading.Thread(target=self._record_thread_worker)
            thread.daemon = False
            thread.start()
            self._record_thread = thread
        else:
            thread = threading.Thread(target=self._record_thread_worker)
            thread.daemon = False
            thread.start()
            self._record_thread = thread

    def _record_thread_worker(self):
        previous_capture = 0
        frames = []

        while not self._kill_thread:
            try:
                if self._live_video.isOpened():
                    grabbed = self._live_video.grab()

                    while not grabbed:
                        print("Reconnecting!")
                        self.__connect()
                        grabbed = self._live_video.grab()

                    tme = time.perf_counter()
                    if tme - previous_capture > 1 / Constants.FRAMERATE:
                        grabbed, frame = self._live_video.read()

                        while not grabbed:
                            print("Reconnecting")
                            self.__connect()
                            grabbed, frame = self._live_video.read()

                        frame = Frame(frame)

                        previous_capture = tme
                        frames.append(frame)

                        if len(frames) >= Constants.DBS:
                            thread = threading.Thread(target=self._observer.observe, args=(frames,))
                            thread.start()
                            frames = [frame]
                else:
                    self.__connect()
            except Exception as e:
                print("Error downloading image from camera {} on ip {}".format(self._place, self._IP))
                print(e)
                self.__connect()

    def __connect(self):
        connected = False
        i = 0
        while not connected:
            try:
                if self._live_video is not None:
                    print("Reconnecting camera at {} on IP {}".format(self._place, self._IP))
                    self._live_video.release()
                    del self._live_video

                self._live_video = cv2.VideoCapture(self._live_video_url, cv2.CAP_FFMPEG)

                connected = True

                print("Connected camera at {} on IP {}".format(self._place, self._IP))
            except Exception:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not connect, retrying in {} seconds".format(seconds))
                time.sleep(seconds)


class FI9803PV3(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place, "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}".
                         format(ip, str(port), user, password),
                         "rtsp://{}:{}@{}:{}/videoMain".format(user, password, ip, str(port + 2)))


class FI89182(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place, "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}".
                         format(ip, str(port), user, password),
                         "http://{}:{}/videostream.cgi?user={}&pwd={}".
                         format(ip, port, Constants.USER, Constants.PASSWORD))

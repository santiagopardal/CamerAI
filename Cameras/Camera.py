import urllib
import io
import time
import cv2
import threading
import Constants
import numpy as np
import requests
from PIL import Image
from Handlers.MotionEventHandler import MotionEventHandler, DiskStoreMotionHandler
from Cameras.Frame import Frame
from Observations.Observers import Observer
from threading import Semaphore
import datetime


class Camera:
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str):
        """
        :param ip: IP of the camera.
        :param port: Port for the camera live stream.
        :param place: Place where the camera is located, this will be the name of the folder where the frames will
        be stored.
        :param screenshot_url: URL to obtain screenshot from the CCTV camera.
        """
        self._IP = ip
        self._port = port
        self._place = place
        self._screenshot_url = screenshot_url
        self._record_thread = None
        self._kill_thread = False
        self._motion_handler = DiskStoreMotionHandler(self._place)
        self._observer = Observer(self)
        self._observe_semaphore = Semaphore(0)
        self._frames_to_observe = []
        self._last_frame = None

    @property
    def place(self) -> str:
        return self._place

    @property
    def ip(self) -> str:
        return self._IP

    @property
    def port(self) -> int:
        return self._port

    @property
    def last_frame(self) -> np.ndarray:
        return self._last_frame

    def set_observer(self, observer: Observer):
        self._observer = observer

    def set_motion_handler(self, motion_handler: MotionEventHandler):
        self._motion_handler = motion_handler

    def __eq__(self, other):
        if isinstance(other, Camera):
            return other.ip == self._IP and other.port == self._port

        return False

    def screenshot(self):
        """
        :return: A screenshot from the camera.
        """
        with urllib.request.urlopen(self._screenshot_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def record(self):
        """
        Starts the recording thread.
        """
        self._record_thread = threading.Thread(target=self._record_thread_worker)
        self._record_thread.start()

    def stop_recording(self):
        """
        Stops recording.
        """
        self._kill_thread = True
        self._record_thread.join()
        self._record_thread = None

    def _record_thread_worker(self):
        """
        Obtains live images from the camera and stores them on self._frames_to_observe so as
        to check whether there has been movement or not in the frames gathered.
        """
        previous_capture = 0
        frames = []

        thread = threading.Thread(target=self._check_movement, args=())
        thread.start()

        start = time.time()

        while not self._kill_thread:
            if time.perf_counter() - previous_capture >= 1 / Constants.FRAMERATE:

                try:
                    previous_capture = time.perf_counter()

                    response = requests.get(self._screenshot_url, stream=True).raw

                    frame = np.asarray(bytearray(response.read()), dtype="uint8")
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                    if frame is not None:
                        self._last_frame = frame
                        frames.append(frame)
                        if len(frames) >= Constants.DBS:
                            end = time.time()
                            true_framerate = Constants.DBS / (end - start)
                            self._frames_to_observe.append((frames, true_framerate))
                            self._observe_semaphore.release()
                            frames = []

                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self._place, self._IP))
                    print(e)

        self._frames_to_observe = []
        self._observe_semaphore.release()

        thread.join()

    @staticmethod
    def _calculate_time_taken(tme, frame_rate, i):
        """
        Approximates the time a frame was taken using the last time an image was received and the framerate.
        :param tme: Last time an image was received.
        :param frame_rate: Frame rate.
        :return: Time the frame was taken approximately.
        """
        return tme + datetime.timedelta(seconds=(1 / frame_rate)*i)

    def _check_movement(self):
        """
        Waits for images to be ready and tells the observer to take a look at them.
        """
        last_frame = None
        last_time_stored = None

        while not self._kill_thread:
            self._observe_semaphore.acquire()

            if self._frames_to_observe:
                """
                Create frames and calculate the time they were taken, this is done here because obtaining the time
                takes a lot of CPU time and it's not worth doing while receiving the frames from the camera. Note that
                the first frame will be the same as the last of the previous batch, so we add the previous frame so as
                to not calculate everything again, including everything needed by the observer, so the last frame
                won't be analysed by the observer until the next batch arrives and will be the first frame of that
                batch. This does not occur on the first run, in which all the frames will be analysed and the last one
                will be analysed twice, on the first run and on the second one, but will be stored only once if needed.
                """
                frames, frame_rate = self._frames_to_observe.pop(0)

                if not last_time_stored:
                    last_time_stored = datetime.datetime.now() - datetime.timedelta(
                        seconds=(Constants.DBS + 1) * (1 / frame_rate))

                frames = [Frame(frame, self._calculate_time_taken(last_time_stored, frame_rate, i+1).time())
                          for i, frame in enumerate(frames)]

                last_time_stored = self._calculate_time_taken(last_time_stored, frame_rate, len(frames))

                lf = frames[len(frames) - 1]

                if last_frame:
                    frames = [last_frame] + frames[:len(frames) - 1]

                movement = self._observer.observe(frames=frames)                       # Pass the frames to the observer
                self._motion_handler.handle(movement)                                  # Handler, manage movement

                last_frame = lf                                                        # update last frame.

                del frames
                del movement

        self._motion_handler.free()


class LiveVideoCamera(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str,
                 screenshot_url: str, live_video_url: str, width: int, height: int):
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
        user = urllib.parse.quote(user)
        password = urllib.parse.quote(password)

        super().__init__(ip, port, place, screenshot_url.format(user, password))

        self._live_video_url = live_video_url.format(user, password)
        self._live_video = None
        self._frame_width = width
        self._frame_height = height
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
        """
        Initializes the recording thread.
        """
        if self._record_thread is not None:
            self._kill_thread = True
            self._record_thread.join()
            self._kill_thread = False

        self._record_thread = threading.Thread(target=self._record_thread_worker)
        self._record_thread.start()

    def _record_thread_worker(self):
        frames = []

        thread = threading.Thread(target=self._check_movement, args=())
        thread.start()

        start = time.time()

        while not self._kill_thread:
            try:
                if self._live_video.isOpened():
                    grabbed, frame = self._live_video.read()                # Read frame

                    while not grabbed:                                      # If could not read frame
                        print("Reconnecting!")
                        self.__connect()                                    # Reconnect
                        grabbed, frame = self._live_video.read()            # Read again, if could not read again retry!

                    frames.append(frame)                                    # Add to list
                    self._last_frame = frame

                    if len(frames) >= Constants.DBS:                        # If we have enough frames to analyse
                        end = time.time()
                        true_framerate = Constants.DBS / (end - start)
                        self._frames_to_observe.append((frames, true_framerate))  # Add them to the queue and
                        self._observe_semaphore.release()                         # wake up observer.
                        frames = []
                        start = end
                else:
                    self.__connect()
            except Exception as e:
                print("Error downloading image from camera {} on ip {}".format(self._place, self._IP))
                print(e)
                self.__connect()

        self._frames_to_observe = []
        self._observe_semaphore.release()

        thread.join()

    def __connect(self):
        """
        Connects to the camera.
        """
        connected = False
        i = 0
        while not connected:
            try:
                if self._live_video is not None:
                    print("Reconnecting camera at {} on IP {}".format(self._place, self._IP))
                    self._live_video.release()
                    del self._live_video

                self._live_video = cv2.VideoCapture(self._live_video_url, cv2.CAP_FFMPEG)
                self._live_video.set(cv2.CAP_PROP_FPS, Constants.FRAMERATE)
                self._live_video.set(cv2.CAP_PROP_FRAME_WIDTH, self._frame_width)
                self._live_video.set(cv2.CAP_PROP_FRAME_HEIGHT, self._frame_height)
                self._live_video.set(cv2.CAP_PROP_BUFFERSIZE, 3)

                connected = True

                print("Connected camera at {} on IP {}".format(self._place, self._IP))
            except:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not connect, retrying in {} seconds".format(seconds))
                time.sleep(seconds)


class FI9803PV3(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        """
        super().__init__(ip, port, place, user, password, "http://{}:{}/{}".
                         format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"),
                         "{}@{}:{}/videoMain".format("rtsp://{}:{}", ip, str(port + 2)),
                         1280, 720)


class FI89182(LiveVideoCamera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        """
        :param ip: IP where the camera is located.
        :param port: Port to connect to camera.
        :param place: Place where the camera is located.
        :param user: Username to connect.
        :param password: Password.
        """
        super().__init__(ip, port, place, user, password,
                         "http://{}:{}/{}".
                         format(ip, str(port), "cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"),
                         "http://{}:{}/{}".
                         format(ip, port, "videostream.cgi?user={}&pwd={}"),
                         640, 480)

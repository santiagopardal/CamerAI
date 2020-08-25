import urllib.request
import io
import datetime
import os
import time
import cv2
import threading
import Constants
from CNNs import create_model
import numpy as np
import requests
from PIL import Image
from MotionEventHandler import MotionEventHandler
from Frame import Frame
import gc


class Camera:
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str):
        self._IP = ip
        self._port = port
        self._place = place
        self._screenshot_url = screenshot_url
        self._record_thread = None
        self._kill_thread = False
        self._neural_network = create_model()
        self._neural_network.load_weights("Neural Network/v4.8.3/model_weights")
        self._motion_handler = MotionEventHandler()

    def get_place(self):
        return self._place

    def set_motion_handler(self, motion_handler: MotionEventHandler):
        self._motion_handler = motion_handler

    def equals(self, cam):
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

    def _handle_new_frames(self, frames):
        i = 1
        previous_frame = frames[0]
        while i < len(frames):
            frame = frames[i]

            movement = self._movement(previous_frame, frame)
            if movement:
                frame.store(self._place + "/")

                if not previous_frame.stored():
                    previous_frame.store(self._place + "/")

                self._motion_handler.handle(frame)

            previous_frame = frame
            i = i + 1

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        pf = previous_frame.get_resized_and_grayscaled()
        frm = frame.get_resized_and_grayscaled()

        diff = cv2.absdiff(pf, frm)
        diff = np.array(diff / 255, dtype="float32")

        images = np.array([diff]).reshape((256, 144, 1))

        movement = self._neural_network.predict_on_batch(np.array([images]))
        gc.collect()

        return movement[0][0] >= Constants.MOVEMENT_SENSITIVITY

    def _store_frame(self, frame, tme):
        try:
            folder = self._place + "/"
            filename = str(tme).replace(":", "-") + ".jpeg"

            if not os.path.exists(folder):
                os.mkdir(folder)

            folder = folder + str(datetime.datetime.now().date()) + "/"

            if not os.path.exists(folder):
                os.mkdir(folder)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame.save(folder + filename, optimize=True, quality=50)
            del frame
        except Exception as e:
            print("Error storing image from camera on {} and ip {}".format(self._place, self._IP))
            print(e)

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
                        if len(frames) >= 50:
                            thread = threading.Thread(target=self._handle_new_frames, args=(frames,))
                            thread.daemon = False
                            thread.start()

                            frames.clear()
                            frames.append(frame)

                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self._place, self._IP))
                    print(e)

            time.sleep(0.001)


class FI9803PV3(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place, "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}".
                         format(ip, str(port), user, password))

        self._live_video_url = "rtsp://{}:{}@{}:{}/videoMain".format(user, password, ip, str(port + 2))
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
       # previous_frame = None
        frames = []

        while not self._kill_thread:
            try:
                if self._live_video.isOpened():
                    ret, frame = self._live_video.read()

                    while not ret:
                        print("Reconnecting!")
                        self.__connect()
<<<<<<< HEAD
                        ret, frame = self._live_video.read()
=======
                        ret, previous_frame = self._live_video.read()
                        frame = previous_frame

                        if frame is not None:
                            previous_frame = Frame(previous_frame)
>>>>>>> origin/master

                    frame = Frame(frame)

                    tme = time.perf_counter()
                    if tme - previous_capture > 1 / Constants.FRAMERATE:
                        previous_capture = tme
                        frames.append(frame)
                        if len(frames) >= 50:
                            thread = threading.Thread(target=self._handle_new_frames, args=(frames,))
                            thread.daemon = False
                            thread.start()

                            frames.clear()
                            frames.append(frame)
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
                if self._live_video is None:
                    self._live_video = cv2.VideoCapture(self._live_video_url)
                else:
                    print("Reconnecting camera at {} on IP {}".format(self._place, self._IP))
                    self._live_video.release()
                    del self._live_video
                    self._live_video = cv2.VideoCapture(self._live_video_url)

                connected = True

                print("Connected camera at {} on IP {}".format(self._place, self._IP))
            except Exception:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not connect, retrying in {} seconds".format(seconds))
                time.sleep(seconds)


class FI89182(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place,
                         "http://{}:{}/snapshot.cgi?user={}&pwd={}&count=0".format(ip, str(port), user, password))

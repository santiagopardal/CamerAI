import urllib.request
from PIL import Image
import io
import datetime
import os
import time
import cv2
import threading
import Constants
from CNNs import create_model
import numpy as np


class Camera:
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str):
        self.IP = ip
        self.port = port
        self.place = place
        self.screenshot_url = screenshot_url
        self.record_thread = None
        self.kill_thread = False
        self.neural_network = create_model()
        self.neural_network.load_weights("Neural Network/model_weights")

    def equals(self, cam):
        return cam.getIP() == self.IP and cam.getPort() == self.port

    def screenshot(self):
        with urllib.request.urlopen(self.screenshot_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def record(self):
        thread = threading.Thread(target=self.__record_thread_worker, args=())
        thread.daemon = False
        thread.start()
        self.record_thread = thread

    def stop_recording(self):
        self.kill_thread = True
        self.record_thread = None

    def _movement(self, previous_frame, frame) -> bool:
        previous_frame = cv2.resize(previous_frame, (256, 144), interpolation=cv2.INTER_AREA)
        previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_RGB2GRAY)

        img = cv2.resize(frame, (256, 144), interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        diff = cv2.absdiff(previous_frame, img)
        diff = np.array(diff / 255, dtype="float32")

        images = np.array([diff]).reshape((256, 144, 1))

        movement = self.neural_network.predict(np.array([images]))

        return movement[0][0] >= 0.6

    def __record_thread_worker(self):
        previous_capture = 0
        while not self.kill_thread:
            if time.time() - previous_capture > 1/Constants.FRAMERATE:
                folder = self.place + "/"
                filename = str(datetime.datetime.now().time()).replace(":", "-") + ".jpeg"

                if not os.path.exists(folder):
                    os.mkdir(folder)

                folder = folder + str(datetime.datetime.now().date()) + "/"
                if not os.path.exists(folder):
                    os.mkdir(folder)

                try:
                    previous_capture = time.time()
                    urllib.request.urlretrieve(self.screenshot_url, folder + filename)
                except Exception as e:
                    print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
                    print(e)

            time.sleep(0.001)


class FI9803PV3(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place, "http://" + ip + ":" + str(port)
                         + "/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=" + user + "&pwd=" + password)

        self.live_video_url = "rtsp://" + user + ":" + password + "@" + ip + ":" + str(port + 2) + "/videoMain"
        self.live_video = None
        self.__connect()

    def record(self):
        try:
            if self.live_video is not None:
                if self.live_video.isOpened():
                    self.__initialize_record_thread()
                else:
                    self.__connect()
                    self.__initialize_record_thread()
            else:
                self.__connect()
                self.__initialize_record_thread()
        except Exception as e:
            while not self.live_video.isOpened():
                print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
                print(e)
                self.__connect()

    def __initialize_record_thread(self):
        if self.record_thread is not None:
            self.kill_thread = True
            self.record_thread.join()
            self.kill_thread = False
            thread = threading.Thread(target=self.__record_thread_worker, args=())
            thread.daemon = False
            thread.start()
            self.record_thread = thread
        else:
            thread = threading.Thread(target=self.__record_thread_worker, args=())
            thread.daemon = False
            thread.start()
            self.record_thread = thread

    def __record_thread_worker(self):
        previous_capture = 0
        previous_frame = None
        while not self.kill_thread:
            try:
                if self.live_video.isOpened():
                    _, frame = self.live_video.read()

                    if previous_frame is None:
                        previous_frame = frame

                    while frame is None:
                        print("Reconnecting!")
                        self.__connect()
                        _, previous_frame = self.live_video.read()
                        frame = previous_frame

                    tme = time.time()
                    if tme - previous_capture > 1/Constants.FRAMERATE:
                        previous_capture = tme
                        thread = threading.Thread(target=self.__store_image, args=(previous_frame, frame, datetime.datetime.now().time()))
                        thread.daemon = False
                        thread.start()

                    previous_frame = frame
                else:
                    self.__connect()
            except Exception as e:
                print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
                print(e)
                self.__connect()

    def __store_image(self, previous_frame, frame, tme):
        movement = self._movement(previous_frame, frame)
        if movement:
            try:
                folder = self.place + "/"
                filename = str(tme).replace(":", "-") + ".jpeg"

                if not os.path.exists(folder):
                    os.mkdir(folder)

                folder = folder + str(datetime.datetime.now().date()) + "/"

                if not os.path.exists(folder):
                    os.mkdir(folder)

                cv2.imwrite(folder + filename, frame)
            except Exception as e:
                print("Error storing image from camera on {} and ip {}".format(self.place, self.IP))
                print(e)

    def __connect(self):
        connected = False
        i = 0
        while not connected:
            try:
                if self.live_video is None:
                    self.live_video = cv2.VideoCapture(self.live_video_url)
                else:
                    print("Reconnecting camera at {} on IP {}".format(self.place, self.IP))
                    self.live_video.release()
                    del self.live_video
                    self.live_video = cv2.VideoCapture(self.live_video_url)

                connected = True

                print("Connected camera at {} on IP {}".format(self.place, self.IP))
            except Exception as e:
                if i < 6:
                    i += 1
                seconds = 2**i
                print("Could not connect, retrying in {} seconds".format(seconds))
                time.sleep(seconds)


class FI89182(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place,
                         "http://" + ip + ":" + str(port) + "/snapshot.cgi?user=" +
                         user + "&pwd=" + password + "&count=0")

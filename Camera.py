import urllib.request
from PIL import Image
import io
import datetime
import os
import cv2


class Camera:
    def __init__(self, ip: str, port: int, place: str, screenshot_url: str):
        self.IP = ip
        self.port = port
        self.place = place
        self.screenshot_url = screenshot_url

    def equals(self, cam):
        return cam.getIP() == self.IP and cam.getPort() == self.port

    def screenshot(self):
        with urllib.request.urlopen(self.screenshot_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def record(self):
        folder = self.place + "/"
        filename = str(datetime.datetime.now().time()).replace(":", "-") + ".jpeg"

        if not os.path.exists(folder):
            os.mkdir(folder)

        folder = folder + str(datetime.datetime.now().date()) + "/"
        if not os.path.exists(folder):
            os.mkdir(folder)

        try:
            urllib.request.urlretrieve(self.screenshot_url, folder + filename)
        except Exception as e:
            print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
            print(e)

        return folder, filename


class FI9803PV3(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place, "http://" + ip + ":" + str(port)
                         + "/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=" + user + "&pwd=" + password)

        self.live_video_url = "rtsp://" + user + ":" + password + "@" + ip + ":" + str(port + 2) + "/videoMain"
        self.live_video = cv2.VideoCapture(self.live_video_url)

    def record(self):
        try:
            if self.live_video.isOpened():
                self.__get_and_store_image()
            else:
                self.live_video = cv2.VideoCapture(self.live_video_url)
                self.__get_and_store_image()
        except Exception as e:
            print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
            print(e)
            self.live_video.release()
            del self.live_video
            self.live_video = cv2.VideoCapture(self.live_video_url)

    def __get_and_store_image(self):
        try:
            _, frame = self.live_video.read()

            folder = self.place + "/"
            filename = str(datetime.datetime.now().time()).replace(":", "-") + ".jpeg"

            if not os.path.exists(folder):
                os.mkdir(folder)

            folder = folder + str(datetime.datetime.now().date()) + "/"

            if not os.path.exists(folder):
                os.mkdir(folder)

            cv2.imwrite(folder + filename, frame)
        except Exception as e:
            print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
            print(e)
            self.live_video.release()
            del self.live_video
            self.live_video = cv2.VideoCapture(self.live_video_url)


class FI89182(Camera):
    def __init__(self, ip: str, port: int, place: str, user: str, password: str):
        super().__init__(ip, port, place,
                         "http://" + ip + ":" + str(port) + "/snapshot.cgi?user=" +
                         user + "&pwd=" + password + "&count=0")

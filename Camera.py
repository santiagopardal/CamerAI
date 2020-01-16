import urllib.request
from PIL import Image
import io
import datetime
import os


class Camera:
    def __init__(self, ip, port, place, image_url):
        self.IP = ip
        self.port = port
        self.place = place
        self.image_url = image_url

    def equals(self, cam):
        return cam.getIP() == self.IP & cam.getPort() == self.port

    def get_image(self):
        with urllib.request.urlopen(self.image_url) as url:
            f = io.BytesIO(url.read())

        image = Image.open(f)

        return image

    def store_live_image(self):
        folder = self.place + "/"
        filename = str(datetime.datetime.now().time()) + ".jpeg"

        if not os.path.exists(folder):
            os.mkdir(folder)

        folder = folder + str(datetime.datetime.now().date()) + "/"
        if not os.path.exists(folder):
            os.mkdir(folder)

        try:
            urllib.request.urlretrieve(self.image_url, folder + filename)
        except Exception as e:
            print("Error downloading image from camera {} on ip {}".format(self.place, self.IP))
            print(e)

        return folder, filename


class FI9803PV3(Camera):
    def __init__(self, ip, port, place):
        super().__init__(ip, port, place, "http://" + ip + ":" + str(port)
                         + "/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=python&pwd=maxithor0057")


class FI89182(Camera):
    def __init__(self, ip, port, place):
        super().__init__(ip, port, place,
                         "http://" + ip + ":" + str(port) + "/snapshot.cgi?user=python&pwd=maxithor0057&count=0")

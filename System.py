import pickle
import os
import time
import threading
import GoogleAPI
from Camera import Camera
import Constants


class System:
    def __init__(self):
        self._last_upload = -4

        if os.path.exists("cameras.pickle"):
            with open("cameras.pickle", "rb") as pck:
                self.cameras = pickle.load(pck)
                pck.close()
        else:
            self.cameras = []
            with open("cameras.pickle", "wb") as pck:
                pickle.dump(self.cameras, pck)
                pck.close()

    def add_camera(self, camera: Camera):
        can_insert = True
        i = 0
        while can_insert and i < len(self.cameras):
            can_insert = self.cameras[i].get_place() != camera.get_place()
            i += 1

        if can_insert:
            self.cameras.append(camera)
#            with open("cameras.pickle", "wb") as pck:
#                pickle.dump(self.cameras, pck)
#                pck.close()

    def remove_camera(self, camera: Camera):
        self.cameras.remove(camera)
        with open("cameras.pickle", "wb") as pck:
            pickle.dump(self.cameras, pck)
            pck.close()

    def run(self):
        for camera in self.cameras:
            camera.record()

        while True:
            print("Sleeping...")
         #   if datetime.datetime.now().hour % 2 == 0 and self._last_upload != datetime.datetime.now().hour:
         #       self._last_upload = datetime.datetime.now().hour
         #       self.__upload_time()

            time.sleep(Constants.UPDATE_EVERY_SECONDS)

    def __upload_time(self):
        print("Upload time!")

        if not os.path.exists("to upload"):
            os.mkdir("to upload")

        for camera in self.cameras:
            if not os.path.exists("to upload/" + camera.place):
                os.mkdir("to upload/" + camera.place)

            thread = threading.Thread(target=self.__upload, args=(camera.place,))
            thread.daemon = True
            thread.start()

    def __upload(self, path: str):
        pass

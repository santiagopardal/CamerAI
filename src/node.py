import os
from src.cameras.serializer import deserialize
import src.constants as constants
import time
from threading import Semaphore
import src.api.cameras as cameras_api


class Node:
    def __init__(self):
        self.cameras = []

        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        self._fetch_cameras_from_api()
        self.waiter = Semaphore(0)

    def run(self):
        for camera in self.cameras:
            camera.receive_video()

        self.waiter.acquire()

        for camera in self.cameras:
            camera.stop_receiving_video()

    def record(self):
        for camera in self.cameras:
            camera.record()

    def stop_recording(self):
        for camera in self.cameras:
            camera.stop_recording()

    def stop(self):
        self.waiter.release()

    def _fetch_cameras_from_api(self):
        i = 0
        cameras = None

        while not cameras:
            try:
                cameras = cameras_api.get_cameras()
                self.cameras = [deserialize(cam=cam) for cam in cameras]
            except Exception:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not fetch from API, retrying in {} seconds".format(seconds))
                time.sleep(seconds)

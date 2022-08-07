import os
from src.cameras.serializer import deserialize
import src.constants as constants
import time
from threading import Semaphore
import src.api.cameras as cameras_api
from src.tcp_listener.tcp_listener import TCPListener


class Node:
    def __init__(self):
        self.cameras = []

        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        self._fetch_cameras_from_api()
        self._listener = TCPListener(self)
        self.waiter = Semaphore(0)

    def run(self):
        self._listener.listen()

        for camera in self.cameras:
            camera.record()
            camera.receive_video()

        self.waiter.acquire()

        for camera in self.cameras:
            camera.stop_recording()
            camera.stop_receiving_video()

        self._listener.stop_listening()

    def stop(self):
        self.waiter.release()

    def record(self):
        for camera in self.cameras:
            camera.record()

    def stop_recording(self):
        for camera in self.cameras:
            camera.stop_recording()

    def add_camera(self, camera: dict):
        camera = deserialize(camera)
        self.cameras.append(camera)
        camera.record()
        camera.receive_video()

    def remove_camera(self, camera_id: int):
        camera = [camera for camera in self.cameras if camera.id == camera_id]
        if camera:
            camera = camera.pop()
            camera.stop_recording()
            camera.stop_receiving_video()
            self.cameras.remove(camera)

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

from src.cameras.serializer import deserialize
import time
from threading import Semaphore
import src.api.api as API
import src.api.node as node_api
import src.api.cameras as cameras_api
from src.tcp_listener.tcp_listener import TCPListener


class Node:
    def __init__(self):
        API.NODE = self
        self._id = None
        self.cameras = []
        self._listener = TCPListener(self)
        self.waiter = Semaphore(0)

        response = node_api.register(self._listener.ip, self._listener.port)
        self._id = response['id']

        self._fetch_cameras_from_api()

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

    @property
    def id(self):
        return self._id

    def _fetch_cameras_from_api(self):
        i = 0
        fetched = False

        while not fetched:
            try:
                cameras = cameras_api.get_cameras()
                self.cameras = [deserialize(cam=cam) for cam in cameras]
                fetched = True
            except Exception as e:
                print(e)
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not fetch from API, retrying in {} seconds".format(seconds))
                time.sleep(seconds)

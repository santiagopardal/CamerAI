import os
from src.cameras.serializer import deserialize
import src.constants as constants
import time
from threading import Semaphore
import src.api.cameras as cameras_api
from src.tcp_listener.tcp_listener import TCPListener
import asyncio


class Node:
    def __init__(self):
        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        self.cameras = []
        self._listener = TCPListener(self)
        self._waiter = Semaphore(0)

    async def run(self):
        print(id(asyncio.get_running_loop()))
        self.cameras = await self._fetch_cameras_from_api()
        self._listener.listen()

        for camera in self.cameras:
            camera.record()
            camera.receive_video()

        self._waiter.acquire()

        for camera in self.cameras:
            camera.stop_recording()
            camera.stop_receiving_video()

        self._listener.stop_listening()

    def stop(self):
        self._waiter.release(1)

    async def record(self):
        for camera in self.cameras:
            camera.record()

    async def stop_recording(self):
        for camera in self.cameras:
            camera.stop_recording()

    async def add_camera(self, camera: dict):
        camera = deserialize(camera)
        self.cameras.append(camera)
        camera.record()
        camera.receive_video()

    async def remove_camera(self, camera_id: int):
        camera = [camera for camera in self.cameras if camera.id == camera_id]
        if camera:
            camera = camera.pop()
            camera.stop_recording()
            camera.stop_receiving_video()
            self.cameras.remove(camera)

    async def _fetch_cameras_from_api(self):
        i = 0
        cameras = None

        while not cameras:
            try:
                cameras = await cameras_api.get_cameras()
                return [deserialize(cam=cam) for cam in cameras]
            except Exception:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not fetch from API, retrying in {} seconds".format(seconds))
                await asyncio.sleep(seconds)

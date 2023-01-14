from src.cameras.serializer import deserialize
from src.cameras import Camera
from threading import Semaphore
import src.api.api as API
import src.api.node as node_api
import src.api.cameras as cameras_api
from src.tcp_listener import TCPListener
import asyncio


class Node:
    def __init__(self):
        API.NODE = self
        self._id = None
        self.cameras = []
        self._listener = TCPListener(self)
        self._waiter = Semaphore(0)

    async def run(self):
        try:
            response = await node_api.register(self._listener.ip, self._listener.port)
            self._id = response['id']
            self.cameras = await self._fetch_cameras_from_api()
            self._listener.listen()

            for camera in self.cameras:
                camera.receive_video()

            self._waiter.acquire()

            for camera in self.cameras:
                camera.stop_recording()
                camera.stop_receiving_video()

            self._listener.stop_listening()
        except Exception as e:
            print(f"Error initializing node, {e}")

    def stop(self):
        self._waiter.release(1)

    def is_recording(self, camera_id: int) -> bool:
        camera = self._get_camera(camera_id)
        return camera.is_recording

    def record(self, cameras_ids: list = None):
        cameras_ids = [int(id) for id in cameras_ids]
        cameras: list[Camera] = [camera for camera in self.cameras
                                 if camera.id in cameras_ids] if cameras_ids else self.cameras
        for camera in cameras:
            camera.record()

    def stop_recording(self, cameras_ids: list = None):
        cameras_ids = [int(id) for id in cameras_ids]
        cameras: list[Camera] = [camera for camera in self.cameras if
                                 camera.id in cameras_ids] if cameras_ids else self.cameras
        for camera in cameras:
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

    def get_snapshot_url(self, camera_id: int):
        camera = self._get_camera(camera_id)
        return camera.snapshot_url

    def _get_camera(self, camera_id: int) -> Camera:
        cameras = [camera for camera in self.cameras if camera.id == int(camera_id)]
        if cameras:
            camera = cameras.pop()
            return camera

        raise Exception('There is no camera with such id')

    @property
    def id(self):
        return self._id

    async def _fetch_cameras_from_api(self):
        i = 0
        cameras = []

        while not cameras:
            try:
                cameras = await cameras_api.get_cameras(self.id)
                return [deserialize(camera) for camera in cameras]
            except Exception as e:
                print(e)
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print(f"Could not fetch from API, retrying in {seconds} seconds")
                await asyncio.sleep(seconds)

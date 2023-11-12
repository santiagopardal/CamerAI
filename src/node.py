from src.cameras.serializer import deserialize
from src.cameras import Camera
import src.api.api as API
from concurrent.futures import ThreadPoolExecutor
import src.api.node as node_api
import src.api.cameras as cameras_api
from src.tcp_listener import LISTENING_PORT
from socket import gethostname, gethostbyname
import time
import logging
from src.constants import NODE_INFO_PATH
import json
import os
from src.Node_pb2_grpc import NodeServicer, add_NodeServicer_to_server
from src.Node_pb2 import CameraIdParameterRequest, URLResponse
import grpc
import google.protobuf.wrappers_pb2 as wrappers


class Node(NodeServicer):
    def __init__(self):
        API.NODE = self
        self._id = None
        self._register()
        self.cameras = self._fetch_cameras_from_api()

    def run(self):
        try:
            logging.info(f"Node running with {len(self.cameras)} cameras.")

            for camera in self.cameras:
                camera.receive_video()

        except Exception as e:
            logging.error(f"Error initializing node, {e}")

    def update_sensitivity(self, request, context):
        camera = self._get_camera(request.camera_id)
        camera.update_sensitivity(request.sensitivity)

    def is_recording(self, request, context) -> bool:
        camera = self._get_camera(request.camera_id)
        return camera.is_recording

    def record(self, request, context):
        cameras_ids = request.cameras_ids
        cameras: list[Camera] = [camera for camera in self.cameras
                                 if camera.id in cameras_ids] if cameras_ids else self.cameras
        for camera in cameras:
            camera.record()

    def stop_recording(self, request, context):
        cameras_ids = request.cameras_ids
        cameras: list[Camera] = [camera for camera in self.cameras if
                                 camera.id in cameras_ids] if cameras_ids else self.cameras
        for camera in cameras:
            camera.stop_recording()

        return {camera_id: False for camera_id in cameras_ids}

    def add_camera(self, camera: dict):
        camera = deserialize(camera)
        self.cameras.append(camera)
        camera.receive_video()

    def remove_camera(self, request, context):
        camera = self._get_camera(request.camera_id)
        camera.stop_recording()
        camera.stop_receiving_video()
        self.cameras.remove(camera)

    def get_snapshot_url(self, request: CameraIdParameterRequest, context) -> URLResponse:
        camera = self._get_camera(request.camera_id)
        return wrappers.StringValue(value=camera.snapshot_url)

    def _get_camera(self, camera_id: int) -> Camera:
        cameras = [camera for camera in self.cameras if camera.id == int(camera_id)]
        if cameras:
            camera = cameras.pop()
            return camera

        raise Exception('There is no camera with such id')

    @property
    def id(self):
        if not self._id and os.path.exists(NODE_INFO_PATH):
            with open(NODE_INFO_PATH) as file:
                data = json.load(file)
                self._id = data['id']

        return self._id

    def _register(self):
        if self.id:
            API.set_headers({"node_id": str(self.id)})

        response = node_api.register(gethostbyname(gethostname()), LISTENING_PORT)
        if not self.id:
            self._id = response['id']
            API.set_headers({"node_id": str(self._id)})
            with open(NODE_INFO_PATH, "w") as node_info_file:
                node_info_file.write(json.dumps({"id": self.id}))

    def _fetch_cameras_from_api(self) -> list:
        i = 0
        cameras = []

        while not cameras:
            try:
                cameras = cameras_api.get_cameras(self.id)
                return [deserialize(camera) for camera in cameras]
            except Exception as e:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                logging.error(f"Could not fetch from API, retrying in {seconds} seconds: {e}")
                time.sleep(seconds)


if __name__ == '__main__':
    logging.basicConfig(
        filename='camerai.log',
        filemode='a',
        level=logging.INFO,
        format="{asctime} {levelname:<8} {message}",
        style="{"
    )

    node = Node()
    node.run()
    server = grpc.server(ThreadPoolExecutor(max_workers=5))
    add_NodeServicer_to_server(node, server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    server.wait_for_termination()

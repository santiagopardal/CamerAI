from src.cameras.serializer import deserialize
from src.cameras import Camera, LiveRetrievalStrategy, RetrievalStrategy
import src.api.api as API
from concurrent.futures import ThreadPoolExecutor
import src.api.node as node_api
import src.api.cameras as cameras_api
from socket import gethostname, gethostbyname
import time
import logging
from src.constants import NODE_INFO_PATH, SECONDS_TO_BUFFER
import json
import os
from src.grpc_protos import Node_pb2_grpc
from src.grpc_protos.Node_pb2_grpc import NodeServicer
from src.grpc_protos.Node_pb2 import (
    CameraIdParameterRequest,
    UpdateSensitivityRequest,
    ManyCameraIdsRequest,
    CameraInfo,
    StreamVideoRequest
)
import grpc
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.empty_pb2 import Empty as EmptyValue

LISTENING_PORT = 50051


class Node(NodeServicer):
    def __init__(self):
        API.NODE = self
        self._id = None
        self._register()
        self.cameras = self._fetch_cameras_from_api()
        self.server = grpc.server(
            ThreadPoolExecutor(max_workers=len(self.cameras) + 1)
        )
        self.video_retrievers: dict[Camera, RetrievalStrategy] = {}

    def run(self):
        try:
            logging.info(f"Node running with {len(self.cameras)} cameras.")

            Node_pb2_grpc.add_NodeServicer_to_server(self, self.server)

            self.server.add_insecure_port(f"0.0.0.0:{LISTENING_PORT}")
            self.server.start()

            for camera in self.cameras:
                self.video_retrievers[camera] = LiveRetrievalStrategy(camera)
                self.video_retrievers[camera].receive_video()

        except Exception as e:
            logging.error(f"Error initializing node, {e}")

    def stop(self, request, context) -> EmptyValue:
        for camera in self.cameras:
            camera.stop_recording()
            self.video_retrievers[camera].stop_receiving_video()

        self.server.stop(None)

        return EmptyValue()

    def update_sensitivity(self, request: UpdateSensitivityRequest, context) -> EmptyValue:
        camera = self._get_camera(request.camera_id)
        camera.update_sensitivity(request.sensitivity)
        return EmptyValue()

    def record(self, request: ManyCameraIdsRequest, context) -> EmptyValue:
        cameras_ids = request.cameras_ids
        cameras: list[Camera] = [
            camera for camera in self.cameras
            if camera.id in cameras_ids
        ] if cameras_ids else self.cameras

        for camera in cameras:
            camera.record()

        logging.info(f"Cameras with id {[id for id in request.cameras_ids]} are going to record video")

        return EmptyValue()

    def stop_recording(self, request: ManyCameraIdsRequest, context) -> EmptyValue:
        cameras_ids = request.cameras_ids
        cameras: list[Camera] = [camera for camera in self.cameras if
                                 camera.id in cameras_ids] if cameras_ids else self.cameras
        for camera in cameras:
            camera.stop_recording()

        return EmptyValue()

    def add_camera(self, request: CameraInfo, context) -> EmptyValue:
        camera = deserialize(
            id=request.id, name=request.name, model=request.model, ip=request.ip, http_port=request.http_port,
            streaming_port=request.streaming_port, user=request.user, password=request.password, width=request.width,
            height=request.height, framerate=request.framerate, recording=request.configurations.recording,
            sensitivity=request.configurations.sensitivity
        )
        self.cameras.append(camera)
        self.video_retrievers[camera] = LiveRetrievalStrategy(camera)
        self.video_retrievers[camera].receive_video()
        logging.info(f"Added camera with id {request.id}")

        return EmptyValue()

    def remove_camera(self, request: CameraIdParameterRequest, context) -> EmptyValue:
        camera = self._get_camera(request.camera_id)
        camera.stop_recording()
        self.video_retrievers[camera].stop_receiving_video()
        self.cameras.remove(camera)
        del self.video_retrievers[camera]
        logging.info(f"Removed camera with id {request.camera_id}")

        return EmptyValue()

    def get_snapshot_url(self, request: CameraIdParameterRequest, context) -> StringValue:
        camera = self._get_camera(request.camera_id)
        return StringValue(value=camera.snapshot_url)

    def stream_video(self, request: StreamVideoRequest, context) -> EmptyValue:
        print(f"Got request to stream video: {request.video_id}")
        return EmptyValue()

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
                return [
                    deserialize(
                        id=camera["id"], name=camera["name"], model=camera["model"], ip=camera["ip"],
                        http_port=camera["http_port"],
                        streaming_port=camera["streaming_port"], user=camera["user"], password=camera["password"],
                        width=camera["width"],
                        height=camera["height"], framerate=camera["framerate"], recording=camera["configurations"]["recording"],
                        sensitivity=camera["configurations"]["sensitivity"]
                    )
                    for camera in cameras
                ]
            except Exception as e:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                logging.error(f"Could not fetch from API, retrying in {seconds} seconds: {e}")
                time.sleep(seconds)

        return []


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
    node.server.wait_for_termination()

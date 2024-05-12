import asyncio
import aiofiles
import cv2
from src.cameras import Camera, SENSITIVITY_UPDATE_EVENT, RECORDING_SWITCHED_EVENT
from src.events_managers.events_manager import get_events_manager
from src.retrieval_strategy import RetrievalStrategy, LiveRetrievalStrategy
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
from google.protobuf.wrappers_pb2 import StringValue, BytesValue
from google.protobuf.empty_pb2 import Empty as EmptyValue

from src.handlers import FrameHandler, BufferedMotionHandler
import src.observations.models.factory as model_factory
from src.observations import DontLookBackObserver


LISTENING_PORT = 50051
_64_KB_IN_BYTES = 64 * 1024


class Node(NodeServicer):
    def __init__(self):
        API.NODE = self
        self._id = None
        self._register()
        self.cameras = self._fetch_cameras_from_api()
        self.server = grpc.aio.server(
            ThreadPoolExecutor(max_workers=len(self.cameras) + 1)
        )
        self.video_retrievers: dict[Camera, RetrievalStrategy] = {}

    async def run(self):
        try:
            logging.info(f"Node running with {len(self.cameras)} cameras.")

            Node_pb2_grpc.add_NodeServicer_to_server(self, self.server)

            self.server.add_insecure_port(f"0.0.0.0:{LISTENING_PORT}")
            await self.server.start()

            for camera in self.cameras:
                frames_handler = self._create_frames_handler_for_camera(camera)
                self.video_retrievers[camera] = LiveRetrievalStrategy(camera, frames_handler)
                self.video_retrievers[camera].receive_video()

        except Exception as e:
            logging.error(f"Error initializing node, {e}")

    async def stop(self, request, context) -> EmptyValue:
        for camera in self.cameras:
            camera.stop_recording()
            self.video_retrievers[camera].stop_receiving_video()

        await self.server.stop(None)

        return EmptyValue()

    async def update_sensitivity(self, request: UpdateSensitivityRequest, context) -> EmptyValue:
        camera = self._get_camera(request.camera_id)
        camera.update_sensitivity(request.sensitivity)
        return EmptyValue()

    async def record(self, request: ManyCameraIdsRequest, context) -> EmptyValue:
        cameras_ids = request.cameras_ids
        cameras: list[Camera] = [
            camera for camera in self.cameras
            if camera.id in cameras_ids
        ] if cameras_ids else self.cameras

        for camera in cameras:
            camera.record()

        logging.info(f"Cameras with id {[id for id in request.cameras_ids]} are going to record video")

        return EmptyValue()

    async def stop_recording(self, request: ManyCameraIdsRequest, context) -> EmptyValue:
        cameras_ids = request.cameras_ids
        cameras: list[Camera] = [camera for camera in self.cameras if
                                 camera.id in cameras_ids] if cameras_ids else self.cameras
        for camera in cameras:
            camera.stop_recording()

        logging.info(f"Cameras with id {[id for id in request.cameras_ids]} stopped recording video")

        return EmptyValue()

    async def add_camera(self, request: CameraInfo, context) -> EmptyValue:
        camera = Camera(**dict(request))
        self.cameras.append(camera)
        frames_handler = self._create_frames_handler_for_camera(camera)
        self.video_retrievers[camera] = LiveRetrievalStrategy(camera, frames_handler)
        self.video_retrievers[camera].receive_video()
        logging.info(f"Added camera with id {request.id}")

        return EmptyValue()

    async def remove_camera(self, request: CameraIdParameterRequest, context) -> EmptyValue:
        camera = self._get_camera(request.camera_id)
        camera.stop_recording()
        self.video_retrievers[camera].stop_receiving_video()
        self.cameras.remove(camera)
        del self.video_retrievers[camera]
        logging.info(f"Removed camera with id {request.camera_id}")

        return EmptyValue()

    async def get_snapshot_url(self, request: CameraIdParameterRequest, context) -> StringValue:
        camera = self._get_camera(request.camera_id)
        return StringValue(value=camera.snapshot_url)

    async def get_snapshot(self, request: CameraIdParameterRequest, context) -> BytesValue:
        camera = self._get_camera(request.camera_id)
        last_snapshot = camera.last_frame

        is_success, buffer = cv2.imencode(".jpg", last_snapshot)

        return BytesValue(value=buffer.tobytes())

    async def stream_video(self, request: StreamVideoRequest, context) -> BytesValue:
        byte_stream_size = min(_64_KB_IN_BYTES, os.path.getsize(request.path))
        async with aiofiles.open(request.path, "rb") as video:
            while byte := await video.read(byte_stream_size):
                yield BytesValue(value=byte)

        os.remove(request.path)

    def _get_camera(self, camera_id: int) -> Camera:
        camera = next(
            (camera for camera in self.cameras if camera.id == int(camera_id)),
            None
        )
        if camera:
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
                return [Camera(**camera) for camera in cameras]
            except Exception as e:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                logging.error(f"Could not fetch from API, retrying in {seconds} seconds: {e}")
                time.sleep(seconds)

        return []

    def _create_frames_handler_for_camera(self, camera: Camera) -> FrameHandler:
        frames_handler = FrameHandler()
        frames_handler.observer = DontLookBackObserver(
            model_factory, camera.configurations.sensitivity
        )
        motion_handler = BufferedMotionHandler(camera, self.id, SECONDS_TO_BUFFER)
        frames_handler.add_motion_handler(motion_handler)
        events_manager = get_events_manager()
        events_manager.subscribe(frames_handler.observer, SENSITIVITY_UPDATE_EVENT, camera)
        events_manager.subscribe(frames_handler, RECORDING_SWITCHED_EVENT, camera)
        return frames_handler


if __name__ == '__main__':
    logging.basicConfig(
        filename='camerai.log',
        filemode='a',
        level=logging.INFO,
        format="{asctime} {levelname:<8} {message}",
        style="{"
    )
    node = Node()
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(node.run())
    loop.run_until_complete(node.server.wait_for_termination())

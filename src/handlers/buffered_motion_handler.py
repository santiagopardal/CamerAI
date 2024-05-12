from src.cameras import Camera
from src.handlers import MotionHandler
from collections import deque
import os
from src.constants import STORING_PATH
from src.media import LocalVideoSaver

from src.message_brokers.message_broker import MessageBrokerPublisher
from src.message_brokers.rabbitmq import get_rabbit_publisher


class BufferedMotionHandler(MotionHandler):
    def __init__(
        self,
        camera: Camera,
        node_id: int,
        seconds_to_buffer: int = 2,
        message_broker_publisher: MessageBrokerPublisher = None
    ):
        self._frames = deque()
        self._frames.append([])
        self._camera = camera
        self._node_id = node_id
        storing_path = os.path.join(STORING_PATH, camera.name)
        self._media_saver = LocalVideoSaver(camera.id, storing_path, camera.framerate)
        self._buffer_size = seconds_to_buffer*camera.framerate

        self._message_broker_publisher = message_broker_publisher or get_rabbit_publisher()

        super().__init__()

    def handle(self, frames: list):
        if frames:
            self._frames[0] = self._frames[0] + frames

            if len(self._frames[0]) >= self._buffer_size:
                to_store = self._frames.popleft()
                self._frames.append([])
                path = self._media_saver.save(to_store)
                self._publish_new_video(path)

    def _publish_new_video(self, path: str):
        path_split = path.split("/")
        payload = {
            "node": self._node_id,
            "camera": self._camera.id,
            "date": path_split[-2],
            "time": path_split[-1].replace(".mp4", "").replace("-", ":"),
            "path": path
        }
        self._message_broker_publisher.publish(
            payload,
            f"{self._camera.id}",
            exchange="camerai"
        )

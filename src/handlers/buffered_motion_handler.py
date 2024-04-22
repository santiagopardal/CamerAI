from src.handlers import MotionHandler
from collections import deque
import os
from src.constants import STORING_PATH
from src.media import MediaSaver
from src.media import RemoteVideoSaver
from src.media import LocalVideoSaver

from src.message_brokers.message_broker import MessageBrokerPublisher
from src.message_brokers.rabbitmq import get_rabbit_publisher


class BufferedMotionHandler(MotionHandler):
    def __init__(
        self,
        camera,
        seconds_to_buffer: int = 2,
        media_saver: MediaSaver = None,
        message_broker_publisher: MessageBrokerPublisher = None
    ):
        self._frames = deque()
        self._frames.append([])
        self._camera = camera
        storing_path = os.path.join(STORING_PATH, camera.name)
        local_video_saver = LocalVideoSaver(camera.id, storing_path, camera.frame_rate)
        self._media_saver = media_saver if media_saver else RemoteVideoSaver(camera.id, local_video_saver)
        self._buffer_size = seconds_to_buffer*camera.frame_rate

        self._message_broker_publisher = message_broker_publisher
        if not message_broker_publisher:
            self._message_broker_publisher = get_rabbit_publisher()

        super().__init__()

    def handle(self, frames: list):
        if frames:
            self._frames[0] = self._frames[0] + frames

            if len(self._frames[0]) >= self._buffer_size:
                to_store = self._frames.popleft()
                self._frames.append([])
                video_id = self._media_saver.save(to_store)
                self._publish_new_video(video_id)

    def _publish_new_video(self, video_id: int):
        self._message_broker_publisher.publish(
            {"video_id": video_id},
            f"{self._camera.id}",
            exchange="camerai"
        )

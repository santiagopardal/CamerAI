import json

from src.handlers import MotionHandler
from collections import deque
import os
from src.constants import STORING_PATH
from src.media import MediaSaver
from src.media import RemoteVideoSaver
from src.media import LocalVideoSaver
from pika import BlockingConnection, ConnectionParameters, PlainCredentials


class BufferedMotionHandler(MotionHandler):
    def __init__(self, camera, seconds_to_buffer: int = 2, media_saver: MediaSaver = None):
        self._frames = deque()
        self._frames.append([])
        self._camera = camera
        storing_path = os.path.join(STORING_PATH, camera.name)
        local_video_saver = LocalVideoSaver(camera.id, storing_path, camera.frame_rate)
        self._media_saver = media_saver if media_saver else RemoteVideoSaver(camera.id, local_video_saver)
        self._buffer_size = seconds_to_buffer*camera.frame_rate
        credentials = PlainCredentials(username=os.environ.get('RABBIT_USER'), password=os.environ.get('RABBIT_PASSWORD'))
        connection_parameters = ConnectionParameters(host=os.environ.get('RABBIT_HOST'), credentials=credentials)
        self._connection = BlockingConnection(connection_parameters)
        # FIXME I need to close the connection and channel at some point
        self._channel = self._connection.channel()

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
        self._channel.exchange_declare(exchange='camerai', exchange_type='direct')
        body = json.dumps({"video_id": video_id})
        self._channel.basic_publish(exchange='camerai', routing_key=f"{self._camera.id}", body=body)
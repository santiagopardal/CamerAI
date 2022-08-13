from src.handlers.motion_handler import MotionHandler
from collections import deque
import os
import asyncio
from src.constants import STORING_PATH
from src.media.savers.media_saver import MediaSaver
from src.media.savers.remote_video_saver import RemoteVideoSaver
from src.media.savers.local_video_saver import LocalVideoSaver


class BufferedMotionHandler(MotionHandler):
    def __init__(self, camera, seconds_to_buffer: int = 2, media_saver: MediaSaver = None):
        self._frames = deque()
        self._frames.append([])
        self._camera = camera
        storing_path = os.path.join(STORING_PATH, camera.name)
        self._media_saver = media_saver if media_saver else RemoteVideoSaver(camera.id, LocalVideoSaver(camera.id, storing_path, camera.frame_rate))
        self._buffer_size = seconds_to_buffer*camera.frame_rate

        super().__init__()

    async def handle(self, frames: list):
        if frames:
            self._frames[0] = self._frames[0] + frames

            if len(self._frames[0]) >= self._buffer_size:
                to_store = self._frames.popleft()
                self._frames.append([])
                asyncio.create_task(self._media_saver.save(to_store))

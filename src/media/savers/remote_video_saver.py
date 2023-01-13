import os
from typing import List
from .media_saver import MediaSaver
from src.media import Frame
import src.api.temporal_videos as temporal_videos_api


class RemoteVideoSaver(MediaSaver):
    def __init__(self, camera_id: int, local_saver: MediaSaver):
        self._camera_id = camera_id
        self._local_saver = local_saver

    async def save(self, frames: List[Frame]):
        path = await self._local_saver.save(frames)
        await temporal_videos_api.upload(self._camera_id, frames[0].date, path)
        os.remove(path)

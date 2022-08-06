import os
from typing import List
from src.media.savers.media_saver import MediaSaver
from src.media.savers.local_video_saver import LocalVideoSaver
from src.media.frame import Frame
import src.api.temporal_videos as temporal_videos_api


class RemoteVideoSaver(MediaSaver):
    def __init__(self, camera_id: int, folder: str, frame_rate: int, local_saver: MediaSaver = None):
        self._folder = folder
        self._frame_rate = frame_rate
        self._camera_id = camera_id
        self._local_saver = local_saver if local_saver else LocalVideoSaver(camera_id, folder, frame_rate)

    def save(self, frames: List[Frame]):
        path = self._local_saver.save(frames)
        temporal_videos_api.upload(self._camera_id, frames[0].date, path)
        os.remove(path)

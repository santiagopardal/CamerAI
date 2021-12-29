import os
from typing import List
from src.media.savers.media_saver import MediaSaver
from src.media.savers.local_video_saver import LocalVideoSaver
from src.media.frame import Frame
import src.api.temporal_videos as temporal_videos


class RemoteVideoSaver(MediaSaver):
    def __init__(self, camera_id: int, folder: str, frame_rate: int):
        self._local_video_saver = LocalVideoSaver(folder, frame_rate)
        self._camera_id = camera_id

    def save(self, frames: List[Frame]):
        path = self._local_video_saver.save(frames)
        temporal_videos.add_temporal_video(self._camera_id, frames[0].date, path, True)
        os.remove(path)

import os
from typing import List
from src.media.savers.local_video_saver import LocalVideoSaver
from src.media.frame import Frame
import src.api.temporal_videos as temporal_videos_api


class RemoteVideoSaver(LocalVideoSaver):
    def save(self, frames: List[Frame]):
        filename = "{}.mp4".format(frames[0].time)
        path = self._store_video(frames, filename)

        temporal_videos_api.add_temporal_video(self._camera_id, frames[0].date, path).json()
        temporal_videos_api.upload(self._camera_id, frames[0].date, path)
        os.remove(path)

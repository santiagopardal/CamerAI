import logging
import os
import cv2
from typing import List
from .media_saver import MediaSaver
from src.media import Frame
import src.api.temporal_videos as temporal_videos_api


class LocalVideoSaver(MediaSaver):
    def __init__(self, camera_id: int, folder: str, frame_rate: int):
        self._folder = folder
        self._frame_rate = frame_rate
        self._camera_id = camera_id
        if not os.path.exists(self._folder):
            os.mkdir(self._folder)

    def save(self, frames: List[Frame]):
        filename = "{}.mp4".format(frames[0].time).replace(":", "-")
        path = self._store_video(frames, filename)
        temporal_videos_api.add_temporal_video(self._camera_id, frames[0].date, path)
        return path

    def _store_video(self, frames: list[Frame], filename: str):
        video_date = frames[0].date

        date_str = f"{video_date.year}-{video_date.month}-{video_date.day}"

        storing_path = os.path.join(self._folder, date_str)

        if not os.path.exists(storing_path):
            os.mkdir(storing_path)

        storing_path = os.path.join(storing_path, filename)
        height, width, layers = frames[0].frame.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(storing_path, fourcc, self._frame_rate, (width, height))

        for frame in frames:
            try:
                video.write(frame.frame)
            except Exception as e:
                logging.error(f"Error storing video: {e}")

        video.release()

        return storing_path

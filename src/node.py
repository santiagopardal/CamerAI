import os
from threading import Thread
from src.cameras.serializer import deserialize
import src.constants as constants
from src.utils.date_utils import get_numbers_as_string
from datetime import timedelta, datetime
import sched
import time
import src.api.videos as videos_api
import src.api.cameras as cameras_api
import src.api.temporal_videos as temporal_videos_api
from libs.VideosMerger.merger import VideoMerger
from libs.VideosMerger.videos_iterator import VideosIterator
import src.media.video.video_factory as video_factory


class Node:
    def __init__(self):
        self.cameras = []

        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        self._fetch_cameras_from_api()

        self.__scheduler = sched.scheduler(time.time, time.sleep)
        self.__schedule_video_transformation()

    def __schedule_video_transformation(self):
        now = datetime.now()
        tomorrow_3_am = now + timedelta(days=1) - timedelta(hours=now.hour) - timedelta(minutes=now.minute) - \
                        timedelta(seconds=now.second) - timedelta(microseconds=now.microsecond) + timedelta(hours=3)

        time_until_3 = tomorrow_3_am - now
        time_until_3 = time_until_3.total_seconds()

        self.__scheduler.enter(time_until_3, 1, self._transform_yesterday_into_video)
        print("Scheduled video transformation in {} seconds!".format(time_until_3))

    def _fetch_cameras_from_api(self):
        """
        Loads cameras from the API.
        """
        i = 0
        cameras = None

        while not cameras:
            try:
                cameras = cameras_api.get_cameras()
                self.cameras = [deserialize(cam=cam) for cam in cameras]
            except Exception:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not fetch from API, retrying in {} seconds".format(seconds))
                time.sleep(seconds)

    def _transform_yesterday_into_video(self):
        self.__schedule_video_transformation()

        yesterday = datetime.now() - timedelta(days=1)

        for camera in self.cameras:
            try:
                self._merge_cameras_video(camera, yesterday)
            except Exception as e:
                print("Error merging videos:", e)

    def _merge_cameras_video(self, camera, date: datetime):
        temporal_videos = temporal_videos_api.get_temporal_videos(camera.id, date)

        pth = os.path.join(constants.STORING_PATH, camera.name)

        day, month, year = get_numbers_as_string(date)
        video_path = "{}/{}-{}-{}.mp4".format(pth, year, month, day)

        videos = VideosIterator(temporal_videos, video_factory)
        merger = VideoMerger(videos)
        merger.merge(video_path, True)

        videos_api.register_new_video(camera.id, date, video_path)

    def record(self):
        """
        Starts recording.
        """
        thread = Thread(target=self._apply_to_all_cameras, args=(lambda cam: cam.record(),))
        thread.start()

    def stop_recording(self):
        """
        Stops recording.
        """
        thread = Thread(target=self._apply_to_all_cameras, args=(lambda cam: cam.stop_recording(),))
        thread.start()

    def _apply_to_all_cameras(self, func):
        """
        Applies a function to all the cameras in the system.
        :param func: function tu apply to all the cameras.
        """
        for camera in self.cameras:
            func(camera)

    def run(self):
        """
        Runs the system.
        """
        for camera in self.cameras:
            camera.receive_video()

        self.__scheduler.run()

        for camera in self.cameras:
            camera.stop_receiving_video()

    def run_n_seconds(self, n):
        """
        Runs for n seconds.
        :param n: Number of seconds to run.
        """
        thread = Thread(target=self.run, args=())
        thread.start()

        time.sleep(n)
        thread.join()

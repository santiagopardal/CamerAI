import os
import threading
import requests
from src.CameraUtils.deserializator import deserialize
import src.constants as constants
from datetime import timedelta
import datetime
import sched
import time
import shutil
from src.VideoUtils.video_utils import *


API_URL = "http://localhost:8080/api"


class System:
    def __init__(self):
        self.cameras = []

        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        self._fetch_cameras_from_api()

        self.__scheduler = sched.scheduler(time.time, time.sleep)
        self.__schedule_video_transformation()

    def __schedule_video_transformation(self):
        now = datetime.datetime.now()
        tomorrow_3_am = now + timedelta(days=1) - timedelta(hours=now.hour) - timedelta(minutes=now.minute) - \
                        timedelta(seconds=now.second) - timedelta(microseconds=now.microsecond) + timedelta(hours=3)

        time_until_3 = tomorrow_3_am - now
        time_until_3 = time_until_3.total_seconds()

        self.__scheduler.enter(time_until_3, 1, self._transform_yesterday_into_video)
        print("Scheduled video transformation in {} seconds!".format(time_until_3))

    def _fetch_cameras_from_api(self):
        """
        Loads cameras from the json file.
        """
        i = 0
        cameras = None

        while not cameras:
            try:
                cameras = requests.get("{}/cameras".format(API_URL)).json()
                self.cameras = [deserialize(cam=cam) for cam in cameras]
            except Exception:
                if i < 6:
                    i += 1
                seconds = 2 ** i
                print("Could not fetch from API, retrying in {} seconds".format(seconds))
                time.sleep(seconds)

    def _transform_yesterday_into_video(self):
        self.__schedule_video_transformation()

        for place in os.listdir(constants.STORING_PATH):
            pth = os.path.join(constants.STORING_PATH, place)

            if os.path.isdir(pth):
                yesterday = datetime.datetime.now() - timedelta(days=1)

                day = yesterday.day if yesterday.day > 9 else "0{}".format(yesterday.day)
                month = yesterday.month if yesterday.month > 9 else "0{}".format(yesterday.month)

                yesterday_path = os.path.join(pth, "{}-{}-{}".format(yesterday.year, month, day))
                video_path = "{}/{}-{}-{}.mp4".format(pth, yesterday.year, month, day)

                self._folder_to_video(yesterday_path, video_path)

    @staticmethod
    def _folder_to_video(folder_path: str, video_path: str):
        print("Creating video on {} at {}, video's path is {}".format(folder_path, datetime.datetime.now().time(), video_path))

        for _, _, day in os.walk(folder_path):
            if len(day) > 0:
                width, height, frame_rate = get_video_properties(os.path.join(folder_path, day[0]))

                result = create_video_writer(video_path, width, height, frame_rate)

                for video in sorted(day):
                    if video.endswith(".mp4"):
                        append_to_video(result, os.path.join(folder_path, video))

                result.release()

                try:
                    shutil.rmtree(folder_path, ignore_errors=True)
                except OSError as e:
                    print("Error deleting folder %s - %s" % (e.filename, e.strerror))

        print("Finished video on {} at {}".format(folder_path, datetime.datetime.now().time()))

    def record(self):
        """
        Starts recording.
        """
        thread = threading.Thread(target=self._apply_to_all_cameras, args=(lambda cam: cam.record(),))
        thread.start()

    def stop_recording(self):
        """
        Stops recording.
        """
        thread = threading.Thread(target=self._apply_to_all_cameras, args=(lambda cam: cam.stop_recording(),))
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
        Runs the system without using GUI.
        """
        for camera in self.cameras:
            camera.receive_video()

        self.__scheduler.run()

        for camera in self.cameras:
            camera.stop_receiving_video()

    def run_n_seconds(self, n):
        """
        Runs without GUI for n seconds.
        :param n: Number of seconds to run.
        """
        thread = threading.Thread(target=self.run, args=())
        thread.start()

        time.sleep(n)
        thread.join()

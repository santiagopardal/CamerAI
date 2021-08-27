import os
import threading
from CameraUtils.Camera.camera import Camera
from CameraUtils.deserializator import deserialize
import constants
from datetime import timedelta
import datetime
from threading import Semaphore
import json
import sched
import time
import shutil
from VideoUtils.video_utils import *


class System:
    def __init__(self):
        self.cameras = []
        self._done_semaphore = Semaphore(0)

        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        if os.path.exists("cameras.json"):
            self._load_cams_from_json_file()

        self.__scheduler = sched.scheduler(time.time, time.sleep)
        self.__schedule_video_transformation()
        self.__scheduler.run(blocking=False)

    def __schedule_video_transformation(self):
        now = datetime.datetime.now()
        tomorrow_3_am = now + timedelta(days=1) - timedelta(hours=now.hour) - timedelta(minutes=now.minute) - \
                        timedelta(seconds=now.second) - timedelta(microseconds=now.microsecond) + timedelta(hours=3)

        time_until_3 = tomorrow_3_am - now
        time_until_3 = time_until_3.total_seconds()

        self.__scheduler.enter(time_until_3, 1, self._transform_yesterday_into_video)
        print("Scheduled video transformation in {} seconds!".format(time_until_3))

    def _save_cams_as_json(self):
        """
        Saves a json file with all the cameras.
        """
        cams = {"cameras": [cam.to_dict() for cam in self.cameras]}

        with open("cameras.json", "w") as json_file:
            json.dump(cams, sort_keys=True, indent=4, fp=json_file)

    def _load_cams_from_json_file(self):
        """
        Loads cameras from the json file.
        """
        with open("cameras.json") as json_file:
            data = json.load(json_file)
            self.cameras = [deserialize(cam=cam) for cam in data["cameras"]]

    def add_cameras(self, cameras: list):
        """
        Adds all the cameras in cameras to the system if they weren't present before.
        :param cameras: CameraUtils to add.
        """
        added = False
        for cam in cameras:
            if cam not in self.cameras:
                self.cameras.append(cam)
                added = True
            else:
                cam.stop_receiving_video()

        if added:
            self._save_cams_as_json()

    def add_camera(self, camera: Camera):
        """
        Adds a camera to the system if not present.
        :param camera: Camera to add.
        """
        if camera not in self.cameras:
            self.cameras.append(camera)

            self._save_cams_as_json()

    def _transform_yesterday_into_video(self):
        for place in os.listdir(constants.STORING_PATH):
            pth = os.path.join(constants.STORING_PATH, place)

            if os.path.isdir(pth):
                yesterday = datetime.datetime.now() - timedelta(days=1)

                day = yesterday.day if yesterday.day > 9 else "0{}".format(yesterday.day)
                month = yesterday.month if yesterday.month > 9 else "0{}".format(yesterday.month)

                yesterday_path = os.path.join(pth, "{}-{}-{}".format(yesterday.year, month, day))
                video_path = "{}/{}-{}-{}.mp4".format(pth, place, yesterday.year, month, day)

                self._folder_to_video(yesterday_path, video_path)

                self.__schedule_video_transformation()

    @staticmethod
    def _folder_to_video(folder_path: str, video_path: str):
        print("Creating video on", folder_path, "name is", video_path)

        for _, _, day in os.walk(folder_path):
            if len(day) > 0:
                width, height, frame_rate = get_video_properties(os.path.join(folder_path, day[0]))

                result = create_video_writer(video_path, width, height, frame_rate)

                for video in day:
                    if video.endswith(".mp4"):
                        append_to_video(result, os.path.join(folder_path, video))

                result.release()

                try:
                    shutil.rmtree(folder_path, ignore_errors=True)
                except OSError as e:
                    print("Error deleting folder %s - %s" % (e.filename, e.strerror))

        print("Finished video on", folder_path)

    def remove_camera(self, camera: Camera):
        """
        Removes a camera from the system if present.
        :param camera: Camera to remove.
        """
        if camera in self.cameras:
            self.cameras.remove(camera)

            self._save_cams_as_json()

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

    def terminate(self):
        """
        Exits the system.
        """
        self._done_semaphore.release()

    def run(self):
        """
        Runs the system without using GUI.
        """
        for camera in self.cameras:
            camera.receive_video()

        self._done_semaphore.acquire()

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
        self._done_semaphore.release()
        thread.join()

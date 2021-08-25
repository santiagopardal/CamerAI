import pickle
import os
import threading
from CameraUtils.Camera.camera import Camera
from CameraUtils.deserializator import deserialize
import constants
from datetime import timedelta
import datetime
from threading import Semaphore
import plotly.express as px
import numpy as np
import json
import sched
import time


class System:
    def __init__(self):
        self.cameras = []
        self._done_semaphore = Semaphore(0)

        if not os.path.exists(constants.STORING_PATH):
            os.mkdir(constants.STORING_PATH)

        if os.path.exists("cameras.json"):
            self._load_cams_from_json_file()

        self.__scheduler = None
        #self.__schedule_video_transformation()

    def __schedule_video_transformation(self):
        if not self.__scheduler:
            self.__scheduler = sched.scheduler(time.time, time.sleep)

        now = datetime.datetime.now()
        tomorrow_3_am = now + timedelta(days=1) - timedelta(hours=now.hour) - timedelta(minutes=now.minute) - \
                        timedelta(seconds=now.second) - timedelta(microseconds=now.microsecond) + timedelta(hours=3)

        time_until_3 = tomorrow_3_am - now
        time_until_3 = time_until_3.total_seconds()

        self.__scheduler.enter(time_until_3, 1, self._transform_yesterday_into_video)
        self.__scheduler.run(blocking=False)

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
                today = datetime.datetime.now()

                day = today.day if today.day > 9 else "0{}".format(today.day)
                month = today.month if today.month > 9 else "0{}".format(today.month)

                yesterday_path = os.path.join(pth, "{}-{}-{}".format(today.year, month, day-1))

                command = 'cat $(find . -maxdepth 1 -name "{}/*.jpeg" | sort -V) | ffmpeg -framerate 23 -i - "{}.mp4"'\
                    .format(yesterday_path,
                            "{}/{} on {}-{}-{}".format(yesterday_path, place, today.year, today.month, today.day - 1)
                            )

                os.system(command)

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

    @staticmethod
    def create_statistics():
        """
        Creates binary file with statistics.
        """
        for place in os.listdir(constants.STORING_PATH):
            place_path = os.path.join(constants.STORING_PATH, place)

            if os.path.isdir(place_path):
                for day in os.listdir(place_path):
                    day_path = os.path.join(place_path, day)
                    if os.path.isdir(day_path):

                        year = int(day[:4])
                        month = int(day[:7][5:])
                        dei = int(day[8:])

                        dates = []

                        for file in os.listdir(day_path):
                            if file.endswith(".jpeg"):
                                file = file[:len(file) - 5]
                                hour = int(file[:2])
                                minute = int(file[:5][3:])
                                seconds = int(float(file[6:]))
                                date = datetime.datetime(year=year, month=month, day=dei,
                                                         hour=hour, minute=minute, second=seconds)
                                dates.append(date)

                        with open(os.path.join(day_path, "statistics.pck"), "wb") as handle:
                            pickle.dump(dates, handle)

    @staticmethod
    def _display_statistics(divisor):
        """
        Displays statistics in web browser.
        """
        for place in os.listdir(constants.STORING_PATH):
            place_path = os.path.join(constants.STORING_PATH, place)

            data = {}

            if os.path.isdir(place_path):
                for day in os.listdir(os.path.join(place_path)):
                    day_path = os.path.join(place_path, day)
                    dates = []

                    if os.path.exists(os.path.join(day_path, "statistics.pck")):
                        with open(os.path.join(day_path, "statistics.pck"), "rb") as handle:
                            dates = pickle.load(handle)

                    starting_hour = 25
                    ending_hour = -1

                    for date in dates:
                        date: datetime.datetime
                        start_of_day = datetime.datetime(date.year, date.month, date.day)

                        if date.hour < starting_hour:
                            starting_hour = date.hour

                        if date.hour > ending_hour:
                            ending_hour = date.hour

                        unit = (date - start_of_day).total_seconds() / divisor
                        unit = round(unit * 10) / 10
                        if unit in data:
                            data[unit] = data[unit] + 1
                        else:
                            data[unit] = 1

                    ending_hour = ending_hour if ending_hour == 24 else ending_hour + 1

                    for i in np.arange(starting_hour, ending_hour, 0.1):
                        i = round(i, 3)
                        if i not in data:
                            data[i] = 0

                vals = [val / len(os.listdir(os.path.join(place_path))) for val in data.values()]
                fig = px.scatter(x=data.keys(), y=vals, title=place + " average")
                fig.show()

    @staticmethod
    def show_statistics():
        """
        Displays statistics in web browser.
        """
        System._display_statistics(60 ** 2)

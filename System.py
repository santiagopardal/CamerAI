import pickle
import os
import time
import threading
from Cameras.Camera import Camera, CameraDeserializator
import Constants
import datetime
from GUI.KivyGUI import CamerAI
from threading import Thread, Semaphore
import plotly.express as px
import numpy as np
import json


class System:
    def __init__(self):
        self._last_upload = -4
        self.cameras = []
        self._gui = None

        self._done_semaphore = Semaphore(0)

        if not os.path.exists(Constants.STORING_PATH):
            os.mkdir(Constants.STORING_PATH)

        if os.path.exists("cameras.json"):
            self._load_cams_from_json_file()

    def _save_cams_as_json(self):
        cams = {"cameras": [cam.to_dict() for cam in self.cameras]}

        with open("cameras.json", "w") as json_file:
            json.dump(cams, sort_keys=True, indent=4, fp=json_file)

    def _load_cams_from_json_file(self):
        with open("cameras.json") as json_file:
            data = json.load(json_file)
            deserializator = CameraDeserializator()
            self.cameras = [deserializator.deserialize(cam=cam) for cam in data["cameras"]]

    def add_cameras(self, cameras: list):
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
        if camera not in self.cameras:
            self.cameras.append(camera)

            self._save_cams_as_json()

    def remove_camera(self, camera: Camera):
        if camera in self.cameras:
            self.cameras.remove(camera)

            self._save_cams_as_json()

    def start_recording(self):
        for camera in self.cameras:
            camera.start_recording()

    def stop_recording(self):
        for camera in self.cameras:
            camera.stop_recording()

    def init_gui(self):
        self._gui = CamerAI(system=self, cameras=self.cameras)
        self._gui.run()

    def terminate(self):
        self._done_semaphore.release()

    def run_with_gui(self):
        t = Thread(target=self.run, args=())
        t.start()

        self.init_gui()

        t.join()

    def run(self):
        for camera in self.cameras:
            camera.receive_video()

        self._done_semaphore.acquire()

        for camera in self.cameras:
            camera.stop_receiving_video()

    def run_n_seconds(self, n):
        thread = threading.Thread(target=self.run, args=())
        thread.start()

        time.sleep(n)
        self._done_semaphore.release()
        thread.join()

    @staticmethod
    def create_statistics():
        for place in os.listdir(Constants.STORING_PATH):
            place_path = os.path.join(Constants.STORING_PATH, place)

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
                                file = file[:len(file)-5]
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
        for place in os.listdir(Constants.STORING_PATH):
            place_path = os.path.join(Constants.STORING_PATH, place)

            data = {}

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
                    unit = round(unit*10)/10
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
    def show_statistics_in_hours():
        System._display_statistics(60**2)

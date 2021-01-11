import pickle
import os
import time
import threading
from Cameras.Camera import Camera
import Constants
import datetime
from GUI.KivyGUI import CamerAI
from threading import Thread, Semaphore
import plotly.express as px


class System:
    def __init__(self):
        self._last_upload = -4
        self.cameras = []
        self._gui = None

        self._done_semaphore = Semaphore(0)

        if not os.path.exists(Constants.STORING_PATH):
            os.mkdir(Constants.STORING_PATH)

        if os.path.exists("cameras.pickle"):
            with open("cameras.pickle", "rb") as pck:
                self.cameras = pickle.load(pck)
                pck.close()

    def update_gui(self):
        for camera in self.cameras:
            self._gui.update(camera.last_frame)

    def add_camera(self, camera: Camera):
        if camera not in self.cameras:
            self.cameras.append(camera)
            # with open("cameras.pickle", "wb") as pck:
            #     pickle.dump(self.cameras, pck)
            #     pck.close()

    def remove_camera(self, camera: Camera):
        self.cameras.remove(camera)
        with open("cameras.pickle", "wb") as pck:
            pickle.dump(self.cameras, pck)
            pck.close()

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

    def __upload_time(self):
        pass

    def __upload(self, path: str):
        pass

    @staticmethod
    def create_statistics():
        for place in os.listdir(Constants.STORING_PATH):
            place_path = os.path.join(Constants.STORING_PATH, place)

            if ".DS" not in place and os.path.isdir(place_path):
                dates_in_place = []

                if os.path.exists(os.path.join(place_path, "dates.pck")):
                    with open(os.path.join(place_path, "dates.pck"), "rb") as handle:
                        dates_in_place = pickle.load(handle)

                for day in os.listdir(place_path):
                    day_path = os.path.join(place_path, day)
                    if ".DS" not in day and os.path.isdir(day_path):

                        year = int(day[:4])
                        month = int(day[:7][5:])
                        dei = int(day[8:])

                        dates = []

                        for file in os.listdir(day_path):
                            if ".DS" not in day:
                                file = file[:len(file)-5]
                                hour = int(file[:2])
                                minute = int(file[:5][3:])
                                seconds = int(float(file[6:]))
                                date = datetime.datetime(year=year, month=month, day=dei,
                                                         hour=hour, minute=minute, second=seconds)
                                dates.append(date)

                        dates_in_place.append(dates)

                with open(os.path.join(place_path, "dates.pck"), "wb") as handle:
                    pickle.dump(dates_in_place, handle)

            print(dates_in_place)

    @staticmethod
    def display_statistics():
        for place in os.listdir(Constants.STORING_PATH):
            place_path = os.path.join(Constants.STORING_PATH, place)

            dates = []
            print(os.path.join(place_path, "dates.pck"))
            if os.path.exists(os.path.join(place_path, "dates.pck")):
                with open(os.path.join(place_path, "dates.pck"), "rb") as handle:
                    dates = pickle.load(handle)

            data = {}

            for lista in dates:
                for date in lista:
                    date: datetime.datetime
                    start_of_day = datetime.datetime(date.year, date.month, date.day)

                    seconds = (date - start_of_day).total_seconds()

                    if seconds in data:
                        data[seconds] += 1
                    else:
                        data[seconds] = 1

            fig = px.scatter(x=[int(val) for val in data.keys()], y=list(data.values()))
            fig.show()

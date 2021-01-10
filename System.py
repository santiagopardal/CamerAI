import pickle
import os
import time
import threading
from Cameras.Camera import Camera
import Constants
import datetime
from GUI.KivyGUI import CamerAI
from threading import Thread, Semaphore


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

import cv2
import CNNs
from Frame import Frame
import Constants
import numpy as np
import datetime
import os
import pickle


class Observer:
    def __init__(self, camera, model=None):
        if model is None:
            self._neural_network = CNNs.create_main_model()
            weights_path = os.path.join("Neural Network", "Second network")
            weights_path = os.path.join(weights_path, "v3")
            weights_path = os.path.join(weights_path, "model")
            self._neural_network.load_weights(weights_path)
        else:
            self._neural_network = model

        self._camera = camera

    def observe(self, frames: list):
        hour = datetime.datetime.now().hour
        if Constants.NIGHT_OBSERVER_SHIFT_HOUR <= hour < Constants.OBSERVER_SHIFT_HOUR:
            self._observe(frames)
        else:
            print("Observer shift, now it's night observer time!")
            observer = NightObserver(self._camera, self._neural_network)
            self._camera.set_observer(observer)
            observer.observe(frames)

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        pf = self._frame_manipulation(previous_frame)
        pf = pf.get_resized_and_grayscaled()

        frm = self._frame_manipulation(frame)
        frm = frm.get_resized_and_grayscaled()

        diff = cv2.absdiff(pf, frm)
        diff = np.array(diff / 255, dtype="float32")

        images = np.array([diff]).reshape(Constants.CNN_INPUT_SHAPE)

        movement = self._neural_network.predict_on_batch(np.array([images]))

        return movement[0][0] >= Constants.MOVEMENT_SENSITIVITY

    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame

    def _observe(self, frames: list):
        i = 1
        recording = False
        storing_path = self._camera.get_place() + "/"
        looked = 0
        bursts = 0

        while i < len(frames):
            frame = frames[i]

            previous_frame = frames[i - 1]
            looked += 1
            if self._movement(previous_frame, frame):
                if not recording:
                    bursts += 1
                    recording = True

                    if i - Constants.JUMP >= 0:
                        last_element = i - Constants.JUMP

                        j = i - 2
                        found_no_movement = False
                        while j > last_element and not found_no_movement:
                            frm = frames[j]
                            pframe = frames[j - 1]
                            looked += 1
                            if self._movement(pframe, frm):
                                frm.store(storing_path)
                                pframe.store(storing_path)
                            else:
                                frames[j].store(storing_path)
                                found_no_movement = True

                            j = j - 2

                        if not found_no_movement and j == last_element - 1:
                            frames[last_element - 1].store(storing_path)
                else:
                    j = i - 2
                    last_element = i - Constants.JUMP

                    while j > last_element:
                        frames[j].store(storing_path)
                        j = j - 1

                frame.store(storing_path)
                previous_frame.store(storing_path)

                if i + 1 < len(frames):
                    frames[i+1].store(storing_path)
            else:
                if recording:
                    recording = False
                    store_all = False
                    j = i - 2
                    last_element = i - Constants.JUMP

                    while j - 1 > last_element and not store_all:
                        frm = frames[j]
                        pframe = frames[j - 1]
                        looked += 1
                        if self._movement(pframe, frm):
                            store_all = True
                        else:
                            j = j - 2

                    if store_all:
                        while j > last_element:
                            frames[j].store(storing_path)
                            frames[j - 1].store(storing_path)
                            j = j - 2

                        frames[i - 1].store(storing_path)

            i = i + Constants.JUMP

        print("Looked {} times with {} bursts on {}".format(looked, bursts, self._camera.get_place()))


class NightObserver(Observer):
    def __init__(self, camera, model=None):
        super().__init__(camera, model)

    def observe(self, frames: list):
        hour = datetime.datetime.now().hour
        if Constants.OBSERVER_SHIFT_HOUR <= hour or hour < Constants.NIGHT_OBSERVER_SHIFT_HOUR:
            self._observe(frames)
        else:
            print("Observer shift")
            observer = Observer(self._camera, self._neural_network)
            self._camera.set_observer(observer)
            observer.observe(frames)

    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame.get_denoised_frame()


class DatasetObserver(Observer):
    def observe(self, frames: list):
        i = 0
        pf = frames[0]
        move = 0
        no_mov = 0
        if not os.path.exists("Movement"):
            os.mkdir("Movement")

        if not os.path.exists("No Movement"):
            os.mkdir("No Movement")

        if not os.path.exists("Movement/list/"):
            os.mkdir("Movement/list/")

        if not os.path.exists("No Movement/list/"):
            os.mkdir("No Movement/list/")

        if not os.path.exists("Movement/list/{}/".format(self._camera.get_place())):
            os.mkdir("Movement/list/{}/".format(self._camera.get_place()))

        if not os.path.exists("No Movement/list/{}/".format(self._camera.get_place())):
            os.mkdir("No Movement/list/{}/".format(self._camera.get_place()))

        for file in os.listdir("Movement/list/{}/".format(self._camera.get_place())):
            try:
                int(file.replace(".pck", ""))
                is_int = True
            except Exception:
                is_int = False
            
            if is_int and int(file.replace(".pck", "")) > move:
                move = int(file.replace(".pck", ""))

        for file in os.listdir("No Movement/list/{}/".format(self._camera.get_place())):
            try:
                int(file.replace(".pck", ""))
                is_int = True
            except Exception:
                is_int = False

            if is_int and int(file.replace(".pck", "")) > no_mov:
                no_mov = int(file.replace(".pck", ""))

        while i < len(frames):
            frame = frames[i]

            if self._movement(pf, frame):
                pf: Frame
                frame: Frame
                a = pf.store("Movement/{}/".format(self._camera.get_place()))
                b = frame.store("Movement/{}/".format(self._camera.get_place()))

                mov = [a, b]

                with open("Movement/list/{}/{}.pck".format(self._camera.get_place(), move), "wb") as handle:
                    pickle.dump(mov, handle)
                    handle.close()
                    del handle
                    del mov

                move += 1
            else:
                a = pf.store("No Movement/{}/".format(self._camera.get_place()))
                b = frame.store("No Movement/{}/".format(self._camera.get_place()))

                mov = [a, b]

                with open("No Movement/list/{}/{}.pck".format(self._camera.get_place(), no_mov), "wb") as handle:
                    pickle.dump(mov, handle)
                    handle.close()
                    del handle
                    del mov

                no_mov += 1

            del pf
            pf = frame
            i += 1

        del frames
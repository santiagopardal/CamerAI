import cv2
import CNNs
from Frame import Frame
import Constants
import numpy as np
import datetime
import tensorflow as tf


class Observer:
    def __init__(self, camera, model=None):
        if model is None:
            self._neural_network = CNNs.create_model()
            self._neural_network.load_weights("Neural Network/v4.8.3/model_weights")
        else:
            self._neural_network = model

        self._camera = camera

    def observe(self, frames: list):
        hour = datetime.datetime.now().hour
        if Constants.OBSERVER_SHIFT_HOUR <= hour <= 23 or 0 <= hour < Constants.NIGHT_OBSERVER_SHIFT_HOUR:
            print("Observer shift, now it's night observer time!")
            observer = NightObserver(self._camera, self._neural_network)
            self._camera.set_observer(observer)
            observer.observe(frames)
        else:
            self._observe(frames)

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        pf = self._frame_manipulation(previous_frame)
        pf = pf.get_resized_and_grayscaled()

        frm = self._frame_manipulation(frame)
        frm = frm.get_resized_and_grayscaled()

        diff = cv2.absdiff(pf, frm)
        diff = np.array(diff / 255, dtype="float32")

        images = np.array([diff]).reshape((256, 144, 1))

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

        print("Looked {} times with {} bursts".format(looked, bursts))


class NightObserver(Observer):
    def __init__(self, camera, model=None):
        super().__init__(camera, model)

    def observe(self, frames: list):
        hour = datetime.datetime.now().hour
        if Constants.NIGHT_OBSERVER_SHIFT_HOUR >= hour < Constants.OBSERVER_SHIFT_HOUR:
            print("Observer shift")
            observer = Observer(self._camera, self._neural_network)
            self._camera.set_observer(observer)
            observer.observe(frames)
        else:
            self._observe(frames)

    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame.get_denoised_frame()
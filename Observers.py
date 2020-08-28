import cv2
import CNNs
from Frame import Frame
import Constants
import numpy as np
import datetime


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
        pf = previous_frame.get_resized_and_grayscaled()
        frm = frame.get_resized_and_grayscaled()

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

        while i < len(frames):
            frame = frames[i]
            frame_manipulated = self._frame_manipulation(frame)

            previous_frame = frames[i-1]
            previous_frame_manipulated = self._frame_manipulation(previous_frame)

            if self._movement(previous_frame_manipulated, frame_manipulated):
                if not recording:
                    recording = True
                    if i-3 >= 0 and i-2 >= 0:
                        frm3 = frames[i-3]
                        frm2 = frames[i-2]

                        manipulated3 = self._frame_manipulation(frm3)
                        manipulated2 = self._frame_manipulation(frm2)

                        if self._movement(manipulated3, manipulated2):
                            if i - 4 >= 0:
                                frames[i-4].store(storing_path)

                            frm3.store(storing_path)
                            frm2.store(storing_path)
                        else:
                            frm2.store(storing_path)

                frame.store(storing_path)
                previous_frame.store(storing_path)

                if i-2 >= 0:
                    frames[i-2].store(storing_path)

                self._camera.handle_motion(frame)
            else:
                if recording:
                    frm3 = frames[i - 3]
                    frm2 = frames[i - 2]

                    manipulated3 = self._frame_manipulation(frm3)
                    manipulated2 = self._frame_manipulation(frm2)

                    if self._movement(manipulated3, manipulated2):
                        frm2.store(storing_path)
                        previous_frame.store(storing_path)

                    frm3.store(storing_path)

                    recording = False

            i = i + 4


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

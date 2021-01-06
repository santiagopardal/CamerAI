import cv2
from Detectors.CNNs import ModelGenerator
from Cameras.Frame import Frame
import Constants
import numpy as np
import datetime
import os
import pickle
import time


class Observer:
    def __init__(self, camera, nn=None):
        """
        :param camera: Camera to observe.
        :param nn: Neural network to detect movement, if not specified will use default.
        """
        if nn is None:
            generator = ModelGenerator()
            self._neural_network = generator.create_main_model()
            self._neural_network.load_weights(Constants.V3_MODEL_WEIGHTS)
        else:
            self._neural_network = nn

        self._camera = camera

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and stores those in which there has been movement. Also checks whether
        it is time to switch observers and does so if needed.
        :param frames: Frames to analyse.
        """
        hour = datetime.datetime.now().hour
        if Constants.NIGHT_OBSERVER_SHIFT_HOUR <= hour < Constants.OBSERVER_SHIFT_HOUR:    # If it is my time to observe
            res = self._observe(frames)                                                    # do so.
        else:                                                                              # If it's not, then
            print("Observer shift, now it's night observer time!")
            observer = NightObserver(self._camera, self._neural_network)
            self._camera.set_observer(observer)                                            # switch observer and
            res = observer.observe(frames)                                                 # observe.

        return res

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        """
        Determines whether there has been movement between two frames.
        :param previous_frame: Frame more distant in time.
        :param frame: Frame nearest in time.
        :return: True if there is movement, False if there is not movement.
        """
        return self._batch_movement_check([(previous_frame, frame)])[0]

    def _frame_manipulation(self, frame: Frame) -> Frame:
        """
        Manipulates the frame, in other words, performs some operation to the frame.
        :param frame: Frame to manipulate.
        :return: Frame manipulated.
        """
        return frame

    def _prepare_for_cnn(self, pf: Frame, frm: Frame):
        """
        Creates and returns an NumPy array with the difference between pf and frm resized, grayscaled and normalized.
        :param pf: Frame more distant in time.
        :param frm: Frame nearest in time.
        :return: NumPy array with the difference between pf and frm resized, grayscaled and normalized.
        """
        pf = self._frame_manipulation(pf)
        pf = pf.get_resized_and_grayscaled()

        frm = self._frame_manipulation(frm)
        frm = frm.get_resized_and_grayscaled()

        diff = cv2.absdiff(pf, frm)
        diff = np.array(diff / 255, dtype="float32").reshape(Constants.CNN_INPUT_SHAPE)

        return diff

    def _batch_movement_check(self, frames: list) -> list:
        """
        Returns a list with the results of checking for all difference in frames if there has been movement or not. By
        difference I mean what _prepare_for_cnn returns.
        :param frames: Frames to analyse.
        :return: List with boolean values representing whether there has been movement or not.
        """
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        movements = self._neural_network.predict_on_batch(np.array(images))

        return [movement[0] >= Constants.MOVEMENT_SENSITIVITY for movement in movements]

    def _observe(self, frames: list) -> list:
        """
        Receives a list of frames and stores those in which there has been movement.
        :param frames: Frames to check movement for.
        """

        start = time.time()
        to_observe = [(frame, frames[i+1]) for i, frame in enumerate(frames) if i % Constants.JUMP == 0]

        results = self._batch_movement_check(to_observe)

        recording = False
        bursts = 0
        looked = len(results)

        frames_with_movement = []

        for i, result in enumerate(results):
            if result:
                if not recording:
                    bursts += 1
                    recording = True

                    if i != 0:
                        last_element = (i - 1)*Constants.JUMP + 1
                        j = i*Constants.JUMP - 1

                        found_no_movement = False

                        while j > last_element and not found_no_movement:
                            frm = frames[j]
                            pframe = frames[j - 1]
                            looked += 1

                            if self._movement(pframe, frm):
                                frames_with_movement.append(frm)
                                frames_with_movement.append(pframe)
                            else:
                                frames_with_movement.append(frames[j])
                                found_no_movement = True

                            j = j - 2

                        if not found_no_movement and j == last_element - 1:
                            frames_with_movement.append(frames[last_element - 1])
                else:
                    j = i*Constants.JUMP - 1
                    last_element = (i - 1)*Constants.JUMP + 2

                    while j > last_element:
                        frames_with_movement.append(frames[j])
                        j = j - 1

                frames_with_movement.append(frames[i*Constants.JUMP + 1])
                frames_with_movement.append(frames[i*Constants.JUMP])

                if i*Constants.JUMP + 2 < len(frames):
                    frames_with_movement.append(frames[i*Constants.JUMP + 2])
            else:
                if recording:
                    recording = False
                    store_all = False
                    j = i*Constants.JUMP - 1
                    last_element = (i - 1) * Constants.JUMP + 1

                    while j - 1 > last_element and not store_all:
                        frm = frames[j]
                        pframe = frames[j - 1]
                        looked += 1
                        if self._movement(pframe, frm):
                            store_all = True
                        else:
                            j = j - 2

                    if store_all:
                        frames_with_movement.append(frames[j + 1])
                        while j > last_element:
                            frames_with_movement.append(frames[j])
                            frames_with_movement.append(frames[j - 1])
                            j = j - 2

        print("Looked at {} FPS, {} times with {} bursts on {}"
              .format(looked / (time.time() - start), looked, bursts, self._camera.place))

        return frames_with_movement


class NightObserver(Observer):
    """
    Observer for when the night comes, it does the same as Observer but denoises the frames
    before analysing.
    This observer is more useful for cameras with low image quality.
    """
    def __init__(self, camera, nn=None):
        super().__init__(camera, nn)

    def observe(self, frames: list) -> list:
        hour = datetime.datetime.now().hour

        if Constants.OBSERVER_SHIFT_HOUR <= hour or hour < Constants.NIGHT_OBSERVER_SHIFT_HOUR: # If it is my time to observe
            res = self._observe(frames)                                                         # do so.
        else:                                                                                   # If it's not, then,
            print("Observer shift")
            observer = Observer(self._camera, self._neural_network)
            self._camera.set_observer(observer)                                                 # switch observer and
            res = observer.observe(frames)                                                      # observe.

        return res

    def _frame_manipulation(self, frame: Frame) -> Frame:
        return frame.get_denoised_frame()


class DatasetObserver(Observer):
    """
    Hardcoded observer for dataset creation don't pay attention to this.
    """
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

        if not os.path.exists("Movement/list/{}/".format(self._camera.place)):
            os.mkdir("Movement/list/{}/".format(self._camera.place))

        if not os.path.exists("No Movement/list/{}/".format(self._camera.place)):
            os.mkdir("No Movement/list/{}/".format(self._camera.place))

        for file in os.listdir("Movement/list/{}/".format(self._camera.place)):
            try:
                int(file.replace(".pck", ""))
                is_int = True
            except Exception:
                is_int = False

            if is_int and int(file.replace(".pck", "")) > move:
                move = int(file.replace(".pck", ""))

        for file in os.listdir("No Movement/list/{}/".format(self._camera.place)):
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
                a = pf.store("Movement/{}/".format(self._camera.place))
                b = frame.store("Movement/{}/".format(self._camera.place))

                mov = [a, b]

                with open("Movement/list/{}/{}.pck".format(self._camera.place, move), "wb") as handle:
                    pickle.dump(mov, handle)
                    handle.close()
                    del handle
                    del mov

                move += 1
            else:
                a = pf.store("No Movement/{}/".format(self._camera.place))
                b = frame.store("No Movement/{}/".format(self._camera.place))

                mov = [a, b]

                with open("No Movement/list/{}/{}.pck".format(self._camera.place, no_mov), "wb") as handle:
                    pickle.dump(mov, handle)
                    handle.close()
                    del handle
                    del mov

                no_mov += 1

            del pf
            pf = frame
            i += 1

        del frames

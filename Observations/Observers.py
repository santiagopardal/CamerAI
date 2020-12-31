import cv2
from Detectors import CNNs
from Cameras.Frame import Frame
import Constants
import numpy as np
import datetime
import os
import pickle


class Observer:
    def __init__(self, camera, nn=None):
        """
        :param camera: Camera to observe.
        :param nn: Neural network to detect movement, if not specified will use default.
        """
        if nn is None:
            self._neural_network = CNNs.create_main_model()
            self._neural_network.load_weights(Constants.V3_MODEL_WEIGHTS)
        else:
            self._neural_network = nn

        self._camera = camera

    def observe(self, frames: list):
        """
        Receives a list of frames and stores those in which there has been movement. Also checks whether
        it is time to switch observers and does so if needed.
        :param frames: Frames to analyse.
        """
        hour = datetime.datetime.now().hour
        if Constants.NIGHT_OBSERVER_SHIFT_HOUR <= hour < Constants.OBSERVER_SHIFT_HOUR:    # If it is my time to observe
            self._observe(frames)                                                          # do so.
        else:                                                                              # If it's not, then
            print("Observer shift, now it's night observer time!")
            observer = NightObserver(self._camera, self._neural_network)
            self._camera.set_observer(observer)                                            # switch observer and
            observer.observe(frames)                                                       # observe.

    def _movement(self, previous_frame: Frame, frame: Frame) -> bool:
        """
        Determines whether there has been movement between two frames.
        :param previous_frame: Frame more distant in time.
        :param frame: Frame nearest in time.
        :return: True if there is movement, False if there is not movement.
        """
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
        """
        Manipulates the frame, in other words, performs some operation to the frame.
        :param frame: Frame to manipulate.
        :return: Frame manipulated.
        """
        return frame

    def _observe(self, frames: list):
        """
        Receives a list of frames and stores those in which there has been movement.
        :param frames: Frames to check movement for.
        """
        i = 1
        recording = False
        storing_path = self._camera.get_place()
        looked = 0
        bursts = 0

        while i < len(frames):
            frame = frames[i]

            previous_frame = frames[i - 1]
            looked += 1
            if self._movement(previous_frame, frame):                      # If there is movement between the two frames
                if not recording:                                          # If we weren't recording then...
                    bursts += 1
                    recording = True

                    if i - Constants.JUMP >= 0:                            # If there are frames before these two, look
                        last_element = i - Constants.JUMP                  # for movement on them to see where the
                                                                           # movement started.
                        j = i - 2
                        found_no_movement = False
                        while j > last_element and not found_no_movement:  # Looking for frames in which there has not
                            frm = frames[j]                                # been movement or we have already analysed.
                            pframe = frames[j - 1]
                            looked += 1
                            if self._movement(pframe, frm):                # If there is movement store them and keep
                                frm.store(storing_path)                    # looking until we reach the last checked or
                                pframe.store(storing_path)                 # we don't find movement anymore.
                            else:                                          # If there is not movement, stop the search
                                frames[j].store(storing_path)              # because we've found the "start of
                                found_no_movement = True                   # movement".

                            j = j - 2

                        if not found_no_movement and j == last_element - 1:  # If we found movement in all the frames
                            frames[last_element - 1].store(storing_path)     # between the "jump", store the frame
                                                                             # prior to the last element.

                else:                                                       # If we were recording then store all the
                    j = i - 2                                               # frames between the jump, included the ones
                    last_element = i - Constants.JUMP                       # analyzed (frame and previous_frame).

                    while j > last_element:
                        frames[j].store(storing_path)
                        j = j - 1

                frame.store(storing_path)
                previous_frame.store(storing_path)

                if i + 1 < len(frames):
                    frames[i+1].store(storing_path)
            else:                                                      # If there is no movement between the two frames.
                if recording:                                          # And we were recording (end of movement)
                    recording = False
                    store_all = False
                    j = i - 2
                    last_element = i - Constants.JUMP

                    while j - 1 > last_element and not store_all:      # Find the end of the movement and store all the
                        frm = frames[j]                                # frames up to the "end of movement".
                        pframe = frames[j - 1]
                        looked += 1
                        if self._movement(pframe, frm):                # If there is movement, store all of the frames
                            store_all = True                           # up to the one in position j (included).
                        else:
                            j = j - 2

                    if store_all:                                      # If we have to store all the frames, then do so.
                        while j > last_element:
                            frames[j].store(storing_path)
                            frames[j - 1].store(storing_path)
                            j = j - 2

                        frames[i - 1].store(storing_path)

            i = i + Constants.JUMP

        print("Looked {} times with {} bursts on {}".format(looked, bursts, self._camera.get_place()))


class NightObserver(Observer):
    """
    Observer for when the night comes, it does the same as Observer but denoises the frames
    before analysing.
    This observer is more useful for cameras with low image quality.
    """
    def __init__(self, camera, nn=None):
        super().__init__(camera, nn)

    def observe(self, frames: list):
        hour = datetime.datetime.now().hour
        if Constants.OBSERVER_SHIFT_HOUR <= hour or hour < Constants.NIGHT_OBSERVER_SHIFT_HOUR: # If it is my time to observe
            self._observe(frames)                                                               # do so.
        else:                                                                                   # If it's not, then,
            print("Observer shift")
            observer = Observer(self._camera, self._neural_network)
            self._camera.set_observer(observer)                                                 # switch observer and
            observer.observe(frames)                                                            # observe.

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
from Observations.Observers.observer import Observer
from Detectors.CNNs import create_tflite_interpreter
import numpy as np
import constants


class LiteObserver(Observer):
    def __init__(self):
        super().__init__()

        self._interpreter = create_tflite_interpreter()

    def _prepare_for_cnn(self, previous_frame, frame):
        res = super()._prepare_for_cnn(previous_frame, frame)

        return np.expand_dims(res, axis=0)

    def _tflite_predict(self, image):
        self._interpreter.set_tensor(self._interpreter.get_input_details()[0]['index'], image)

        self._interpreter.invoke()

        output_data = self._interpreter.get_tensor(self._interpreter.get_output_details()[0]['index'])
        results = np.squeeze(output_data)

        return results

    def _batch_movement_check(self, frames: list) -> list:
        """
        Returns a list with the results of checking for all difference in frames if there has been movement or not. By
        difference I mean what _prepare_for_cnn returns.
        :param frames: List of frames to analyse.
        :return: List with boolean values representing whether there has been movement or not.
        """
        images = [self._prepare_for_cnn(pf, frm) for pf, frm in frames]

        return [self._tflite_predict(image) >= constants.MOVEMENT_SENSITIVITY for image in images]

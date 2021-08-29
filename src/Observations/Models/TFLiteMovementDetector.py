from src.Observations.Models.model import Model
from tflite_runtime.interpreter import Interpreter
from src import constants
import numpy as np


class TFLiteModelDetector(Model):
    def __init__(self, tflite_model_path=constants.LITE_MODEL_PATH):
        super().__init__()

        self._interpreter = Interpreter(model_path=tflite_model_path)
        self._interpreter.allocate_tensors()

    def predict(self, data) -> float:
        self._interpreter.set_tensor(self._interpreter.get_input_details()[0]['index'], data)

        self._interpreter.invoke()

        output_data = self._interpreter.get_tensor(self._interpreter.get_output_details()[0]['index'])

        return float(np.squeeze(output_data))

    def predict_on_batch(self, data) -> list:
        return [self.predict(dta) for dta in data]

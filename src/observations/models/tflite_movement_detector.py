from src.observations.models.model import Model
from src import constants
import numpy as np
from threading import Lock
try:
    from tensorflow.lite.python.interpreter import Interpreter
except:
    from tflite_runtime.interpreter import Interpreter


class TFLiteModelDetector(Model):

    _instance = None
    _mutex = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, tflite_model_path=constants.LITE_MODEL_PATH):
        super().__init__()
        self._mutex = Lock()
        self._interpreter = Interpreter(model_path=tflite_model_path)
        self._interpreter.allocate_tensors()

    def predict(self, data) -> float:
        return self.predict_on_batch([data])[0]

    def predict_on_batch(self, data) -> list:
        self._mutex.acquire()
        result = [self._predict(dta) for dta in data]
        self._mutex.release()
        return result

    def _predict(self, data) -> float:
        self._interpreter.set_tensor(self._interpreter.get_input_details()[0]['index'], data)

        self._interpreter.invoke()

        output_data = self._interpreter.get_tensor(self._interpreter.get_output_details()[0]['index'])

        return float(np.squeeze(output_data))

from .model import Model
import numpy as np
import tensorflow as tf
from tensorflow_addons.metrics import F1Score
from src.constants import TATIANA


class Tatiana(Model):
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._model is None:
            # FIXME Remove custom objects from model
            custom_objects = {'f1_score': F1Score(num_classes=1, threshold=0.5)}
            cls._model = tf.keras.models.load_model(TATIANA, custom_objects=custom_objects)

        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__()

    def predict(self, data) -> float:
        return self.predict_on_batch([data])[0]

    def predict_on_batch(self, data) -> list:
        return self._model(np.array(data))

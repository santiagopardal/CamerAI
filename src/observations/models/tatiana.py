from keras.src.metrics import F1Score
from numpy import ndarray

from .model import Model
import numpy as np
import tensorflow as tf
from src.constants import TATIANA


class Tatiana(Model):
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._model is None:
            # FIXME Remove custom objects from model
            custom_objects = {"f1_score": F1Score(num_classes=1, threshold=0.5)}
            cls._model = tf.keras.models.load_model(TATIANA, custom_objects=custom_objects)

        return super().__new__(cls, *args, **kwargs)

    def predict(self, data: ndarray) -> float:
        return self.predict_on_batch([data])[0]

    def predict_on_batch(self, data: list[ndarray]) -> list[float]:
        return self._model.predict(np.array(data))

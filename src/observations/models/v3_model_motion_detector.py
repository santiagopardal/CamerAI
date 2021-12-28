from src.observations.models.model import Model
from src import constants
import numpy as np
import tensorflow as tf
from src.constants import CNN_INPUT_SHAPE


def create_lite_model():
    _model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32, kernel_size=(5, 5), padding="same",
                               activation="relu", input_shape=CNN_INPUT_SHAPE),
        tf.keras.layers.MaxPooling2D(pool_size=5, strides=3),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv2D(32, kernel_size=(7, 7), padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=7, strides=3),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv2D(64, kernel_size=(7, 7), padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=7, strides=3),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(0.5),

        tf.keras.layers.Dense(1024, activation="relu"),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-64)
    loss = tf.keras.losses.BinaryCrossentropy()

    _model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])
    _model.load_weights(constants.TINY_MODEL_WEIGHTS)

    _model.predict(
        np.array([np.array([[180]*CNN_INPUT_SHAPE[0]]*CNN_INPUT_SHAPE[1])
                 .reshape(constants.CNN_INPUT_SHAPE)])
    )

    return _model


class V3MotionDetector(Model):
    _model = None

    def __new__(cls, *args, **kwargs):
        if cls._model is None:
            cls._model = create_lite_model()

        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__()

    def predict(self, data) -> float:
        return self.predict_on_batch([data])[0]

    def predict_on_batch(self, data) -> list:
        return self._model(np.array(data))

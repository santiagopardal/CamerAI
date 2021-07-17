import tensorflow as tf
from threading import Lock
import constants
import numpy as np


physical_devices = tf.config.experimental.list_physical_devices('GPU')

if len(physical_devices) > 0:
    for device in physical_devices:
        config = tf.config.experimental.set_memory_growth(device, True)

_mutex = Lock()
_model = None


def create_lite_model():
    global _model
    global _mutex

    with _mutex:
        if _model is None:
            _model = tf.keras.models.Sequential([

                tf.keras.layers.Conv2D(32, kernel_size=(5, 5), padding="same", activation="relu", input_shape=(180, 180, 1)),
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

            optimizer = tf.keras.optimizers.Adam(lr=1e-64)
            loss = tf.keras.losses.BinaryCrossentropy()

            _model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])
            _model.load_weights(constants.TINY_MODEL_WEIGHTS)
            _model.predict(np.array([np.array([[180]*180]*180).reshape(constants.CNN_INPUT_SHAPE)]))

    return _model


def create_main_model():
    """
    Generates the main model.
    :return: Model created.
    """
    global _model
    global _mutex

    with _mutex:
        if _model is None:
            _model = tf.keras.models.Sequential([

                tf.keras.layers.Conv2D(64, kernel_size=(5, 5), padding="same", activation="relu", input_shape=(180, 180, 1)),
                tf.keras.layers.MaxPooling2D(pool_size=5, strides=3),
                tf.keras.layers.Dropout(0.25),
                tf.keras.layers.BatchNormalization(),

                tf.keras.layers.Conv2D(64, kernel_size=(5, 5), padding="same", activation="relu"),
                tf.keras.layers.MaxPooling2D(pool_size=5, strides=2),
                tf.keras.layers.Dropout(0.25),
                tf.keras.layers.BatchNormalization(),

                tf.keras.layers.Conv2D(128, kernel_size=(5, 5), padding="same", activation="relu"),
                tf.keras.layers.MaxPooling2D(pool_size=5, strides=2),
                tf.keras.layers.Dropout(0.1),
                tf.keras.layers.BatchNormalization(),

                tf.keras.layers.Conv2D(256, kernel_size=(5, 5), padding="same", activation="relu"),
                tf.keras.layers.MaxPooling2D(pool_size=5, strides=3),

                tf.keras.layers.Flatten(),
                tf.keras.layers.Dropout(0.5),

                tf.keras.layers.Dense(2304, activation="relu"),
                tf.keras.layers.Dense(512, activation="relu"),
                tf.keras.layers.Dense(1, activation="sigmoid")
            ])

            optimizer = tf.keras.optimizers.Adam(lr=1e-50)
            loss = tf.keras.losses.BinaryCrossentropy()

            _model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])
            _model.load_weights(constants.V3_MODEL_WEIGHTS)

    return _model

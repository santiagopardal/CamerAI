import tensorflow as tf
from threading import Lock
import Constants


physical_devices = tf.config.experimental.list_physical_devices('GPU')

if len(physical_devices) > 0:
    config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

mutex = Lock()
model = None


def create_main_model():
    """
    Generates the main model.
    :return: Model created.
    """
    global model
    global mutex
    mutex.acquire()

    if model is None:
        model = tf.keras.models.Sequential([

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

        model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])
        model.load_weights(Constants.V3_MODEL_WEIGHTS)

    mutex.release()

    return model

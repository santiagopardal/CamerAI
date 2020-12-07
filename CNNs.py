import tensorflow as tf


def create_model():
    model = tf.keras.models.Sequential([

        tf.keras.layers.Conv2D(64, kernel_size=(5, 5), activation="relu", input_shape=(256, 144, 30)),
        tf.keras.layers.MaxPooling2D(pool_size=3, strides=2),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv2D(64, kernel_size=(5, 5), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=3, strides=2),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv2D(128, kernel_size=(5, 5), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=3, strides=2),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv2D(256, kernel_size=(5, 5), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=2, strides=2),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(0.5),

        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])

    optimizer = tf.keras.optimizers.Adam(lr=1e-5)
    loss = tf.keras.losses.BinaryCrossentropy()

    model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])

    return model


def create_3d_model():
    model = tf.keras.models.Sequential([

        tf.keras.layers.Conv3D(64, kernel_size=(5, 5), activation="relu", input_shape=(256, 144, 1)),
        tf.keras.layers.MaxPooling3D(pool_size=3, strides=2),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv3D(64, kernel_size=(5, 5), activation="relu"),
        tf.keras.layers.MaxPooling3D(pool_size=3, strides=2),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv3D(128, kernel_size=(5, 5), activation="relu"),
        tf.keras.layers.MaxPooling3D(pool_size=3, strides=2),
        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Conv3D(256, kernel_size=(5, 5), activation="relu"),
        tf.keras.layers.MaxPooling3D(pool_size=2, strides=2),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(0.5),

        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])

    optimizer = tf.keras.optimizers.Adam(lr=1e-2)
    loss = tf.keras.losses.BinaryCrossentropy()

    model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])

    return model

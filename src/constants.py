from pathlib import Path

import numpy as np
from numpy import sqrt
import os

from src import config

DETECTION_BATCH_SIZE = config.get_settings().DETECTION_BATCH_SIZE


def cost_function(b):
    return DETECTION_BATCH_SIZE / b + 1 + MOVEMENT_BURSTS * (b - 1)


def cost_derivative(b):
    return MOVEMENT_BURSTS - DETECTION_BATCH_SIZE / (b**2)


def calculate_jump():
    res = round(sqrt(DETECTION_BATCH_SIZE / MOVEMENT_BURSTS))

    vals = np.array([cost_function(res - 1), cost_function(res), cost_function(res + 1)])

    return res + (np.argmin(vals) - 1)


def calculate_dbs():
    if DETECTION_BATCH_SIZE % JUMP == 0:
        return DETECTION_BATCH_SIZE + 2
    else:
        return round(JUMP * round(DETECTION_BATCH_SIZE / JUMP)) + 2


FRAME_RATE = 23

MOVEMENT_SENSITIVITY = 0.5
MOVEMENT_BURSTS = 2
SECONDS_TO_BUFFER = 2

JUMP = calculate_jump()
DBS = calculate_dbs()

RESOLUTION = (180, 180)
CNN_INPUT_SHAPE = (180, 180, 1)

ABSOLUTE_PATH = Path(__file__).parent.parent

NODE_INFO_PATH = os.path.join(ABSOLUTE_PATH, "node.json")

STORING_PATH = os.path.join(ABSOLUTE_PATH, "Images")

AI_PATH = os.path.join(ABSOLUTE_PATH, "ai")

LITE_MODEL_PATH = os.path.join(AI_PATH, "lite")
LITE_MODEL_PATH = os.path.join(LITE_MODEL_PATH, "model.tflite")

TATIANA = os.path.join(AI_PATH, "Tatiana")

if not os.path.exists(STORING_PATH):
    os.mkdir(STORING_PATH)

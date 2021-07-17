import numpy as np
from numpy import sqrt
import os


def cost_function(b):
    return DETECTION_BATCH_SIZE / b + 1 + MOVEMENT_BURSTS * (b-1)


def cost_derivative(b):
    return MOVEMENT_BURSTS - DETECTION_BATCH_SIZE/(b**2)


def calculate_jump():
    res = round(sqrt(DETECTION_BATCH_SIZE / MOVEMENT_BURSTS))

    vals = np.array([cost_function(res - 1), cost_function(res), cost_function(res + 1)])

    return res + (np.argmin(vals) - 1)


def calculate_dbs():
    if DETECTION_BATCH_SIZE % JUMP == 0:
        return DETECTION_BATCH_SIZE + 2
    else:
        return round(JUMP * round(DETECTION_BATCH_SIZE/JUMP)) + 2


FRAMERATE = 23

MOVEMENT_SENSITIVITY = 0.84
DETECTION_BATCH_SIZE = 92
MOVEMENT_BURSTS = 2

JUMP = calculate_jump()
DBS = calculate_dbs()

RESOLUTION = (180, 180)
CNN_INPUT_SHAPE = (180, 180, 1)

ABSOLUTE_PATH = os.path.abspath(os.path.curdir)

STORING_PATH = os.path.join(ABSOLUTE_PATH, "Images")

V3_MODEL_WEIGHTS = os.path.join(ABSOLUTE_PATH, "Neural Network")
TINY_MODEL_WEIGHTS = os.path.join(V3_MODEL_WEIGHTS, "tiny")
TINY_MODEL_WEIGHTS = os.path.join(TINY_MODEL_WEIGHTS, "model")
V3_MODEL_WEIGHTS = os.path.join(V3_MODEL_WEIGHTS, "Second network")
V3_MODEL_WEIGHTS = os.path.join(V3_MODEL_WEIGHTS, "v3")
V3_MODEL_WEIGHTS = os.path.join(V3_MODEL_WEIGHTS, "model")

YOLO_V3_PATH = os.path.join(ABSOLUTE_PATH, "YOLO v3")
YOLO_V4_PATH = os.path.join(ABSOLUTE_PATH, "YOLO v4")

YOLO_V3_TINY_PATH = os.path.join(YOLO_V3_PATH, "tiny")
YOLO_V3_TINY_WEIGHTS = os.path.join(YOLO_V3_TINY_PATH, "yolov3.weights")
YOLO_V3_TINY_CONFIGS = os.path.join(YOLO_V3_TINY_PATH, "yolov3.cfg")
YOLO_V3_TINY_RESOLUTION = 448


YOLO_V3_WEIGHTS = os.path.join(YOLO_V3_PATH, os.path.join("320", "yolov3.weights"))
YOLO_V3_CONFIGS = os.path.join(YOLO_V3_PATH, os.path.join("320", "yolov3.cfg"))
YOLO_V3_RESOLUTION = 320

YOLO_V4_TINY_PATH = os.path.join(YOLO_V4_PATH, "tiny")

YOLO_V4_TINY_WEIGHTS = os.path.join(YOLO_V4_TINY_PATH, "yolov4.weights")
YOLO_V4_TINY_CONFIGS = os.path.join(YOLO_V4_TINY_PATH, "yolov4.cfg")
YOLO_V4_TINY_RESOLUTION = 448

YOLO_V4_WEIGHTS = os.path.join(YOLO_V3_PATH, os.path.join("320", "yolov4.weights"))
YOLO_V4_CONFIGS = os.path.join(YOLO_V3_PATH, os.path.join("320", "yolov4.cfg"))
YOLO_V4_RESOLUTION = 320


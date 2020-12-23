from scipy.optimize import fsolve
from numpy import log, power


def cost_function(b):
    if b > 3:
        return DETECTION_BATCH_SIZE / b + 1 + MOVEMENT_BURSTS * power(2, b - 3)
    else:
        return DETECTION_BATCH_SIZE / b + 1 + MOVEMENT_BURSTS


def cost_derivative(b):
    if b > 3:
        return log(2) * power(2, b - 3) * MOVEMENT_BURSTS - DETECTION_BATCH_SIZE / power(b, 2)
    else:
        return log(2) * MOVEMENT_BURSTS - DETECTION_BATCH_SIZE / power(b, 2)


def calculate_jump():
    b = 0
    if MOVEMENT_BURSTS/DBS >= 0.9:
        b = 1
    else:
        b = round(fsolve(cost_derivative, 4)[0])
        if cost_function(b) >= cost_function(b+1):
            if cost_function(b + 1) <= cost_function(b - 1):
                b = b + 1
            else:
                b = b - 1
        else:
            if cost_function(b) > cost_function(b - 1):
                b = b - 1

    return b


FRAMERATE = 24

UPDATE_EVERY_SECONDS = 300

USER = "admin"
PASSWORD = "*{-4s#aG*_>2"

OBSERVER_SHIFT_HOUR = 19
NIGHT_OBSERVER_SHIFT_HOUR = 6

MOVEMENT_SENSITIVITY = 0.6
DETECTION_BATCH_SIZE = 100
MOVEMENT_BURSTS = 1

DBS = DETECTION_BATCH_SIZE + 2
JUMP = calculate_jump()

RESOLUTION = (180, 180)
CNN_INPUT_SHAPE = (180, 180, 1)

YOLO_V3_TINY_WEIGHTS = "./YOLO v4/tiny/yolov4.weights"
YOLO_V3_TINY_CONFIGS = "./YOLO v4/tiny/yolov4.cfg"
YOLO_V3_TINY_RESOLUTION = 448

YOLO_V3_WEIGHTS = "./YOLO v4/320/yolov4.weights"
YOLO_V3_CONFIGS = "./YOLO v4/320/yolov4.cfg"
YOLO_V3_RESOLUTION = 320

YOLO_V4_TINY_WEIGHTS = "./YOLO v4/tiny/yolov4.weights"
YOLO_V4_TINY_CONFIGS = "./YOLO v4/tiny/yolov4.cfg"
YOLO_V4_TINY_RESOLUTION = 416

YOLO_V4_WEIGHTS = "./YOLO v4/320/yolov4.weights"
YOLO_V4_CONFIGS = "./YOLO v4/320/yolov4.cfg"
YOLO_V4_RESOLUTION = 320

from scipy.optimize import fsolve
from numpy import log, power
import time


def cost_derivative(b):
    if b > 3:
        return log(2) * power(2, b - 3) * MOVEMENT_BURSTS - DETECTION_BATCH_SIZE / power(b, 2)
    else:
        return log(2) * MOVEMENT_BURSTS - DETECTION_BATCH_SIZE / power(b, 2)


FRAMERATE = 24

UPDATE_EVERY_SECONDS = 300

USER = "admin"
PASSWORD = "maxi7500"

OBSERVER_SHIFT_HOUR = 19
NIGHT_OBSERVER_SHIFT_HOUR = 6

MOVEMENT_SENSITIVITY = 0.83
DETECTION_BATCH_SIZE = 105
MOVEMENT_BURSTS = 2
JUMP = 1 if MOVEMENT_BURSTS/DETECTION_BATCH_SIZE > 0.9 else round(fsolve(cost_derivative, 1)[0])

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

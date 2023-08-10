from numpy import ndarray
from cv2 import resize, cvtColor, INTER_AREA, COLOR_RGB2GRAY


def resize_frame(frame: ndarray, resolution: tuple) -> ndarray:
    return resize(frame, resolution, interpolation=INTER_AREA)


def black_and_white(frame: ndarray) -> ndarray:
    return cvtColor(frame, COLOR_RGB2GRAY)


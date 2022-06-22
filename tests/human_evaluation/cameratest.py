import cv2
import numpy as np
import urllib
import concurrent.futures
from src.observations.models.tatiana import Tatiana
from src.constants import CNN_INPUT_SHAPE, MOVEMENT_SENSITIVITY


MODEL = Tatiana()
POOL = concurrent.futures.ThreadPoolExecutor(5)
CAMERA_URL = "rtsp://{}:{}@192.168.0.131:554/videoMain".format(urllib.parse.quote("admin"), urllib.parse.quote("*{-4s#aG*_>2"))


def resize(frame):
    return cv2.resize(frame, (CNN_INPUT_SHAPE[0], CNN_INPUT_SHAPE[1]), interpolation=cv2.INTER_AREA)


def resize_and_grayscale(frame):
    img = resize(frame=frame)
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def get_diff(previous_frame, frame):
    previous_frame = resize_and_grayscale(previous_frame)
    img = resize_and_grayscale(frame)
    return cv2.absdiff(img, previous_frame)


def detect_movement(diff):
    diff = np.array(diff / 255, dtype="float32")
    images = np.array([diff]).reshape(CNN_INPUT_SHAPE)
    movement = MODEL.predict(images)
    if movement >= 0.5:
        print(movement)


def diff_without_resize(previous, actual):
    previous = cv2.cvtColor(previous, cv2.COLOR_RGB2GRAY)
    actual = cv2.cvtColor(actual, cv2.COLOR_RGB2GRAY)
    return cv2.absdiff(actual, previous)


def show_video():
    cap = cv2.VideoCapture(CAMERA_URL)

    _, previous_image = cap.read()
    close = False

    while cap.isOpened() and not close:
        ret, frame = cap.read()

        cv2.imshow('Video', frame)
        diff = diff_without_resize(previous_image, frame)
        cv2.imshow('Diff', diff)
        diff = resize(diff)
        cv2.imshow('CNN', diff)

        POOL.submit(detect_movement, diff)
        previous_image = frame

        if cv2.waitKey(20) & 0xFF == ord('q'):
            close = True

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    show_video()

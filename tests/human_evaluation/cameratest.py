import cv2
import numpy as np
import threading
import urllib
from src.observations.models.v3_model_motion_detector import V3MotionDetector


detector = V3MotionDetector()


def resize(frame):
    return cv2.resize(frame, (180, 180), interpolation=cv2.INTER_AREA)


def resize_and_grayscale(frame):
    img = cv2.resize(frame, (180, 180), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def get_diff(previous_frame, frame):
    previous_frame = resize_and_grayscale(previous_frame)
    img = resize_and_grayscale(frame)

    return cv2.absdiff(img, previous_frame)


def detect_movement(diff):
    diff = np.array(diff / 255, dtype="float32")

    images = np.array([diff]).reshape((180, 180, 1))

    movement = detector.predict(images)

    if movement >= 0.6:
        print(movement)


def diff_without_resize(previous, actual):
    previous = cv2.cvtColor(previous, cv2.COLOR_RGB2GRAY)
    actual = cv2.cvtColor(actual, cv2.COLOR_RGB2GRAY)
    return cv2.absdiff(actual, previous)


def show_video():
    url = "rtsp://{}:{}@192.168.0.131:554/videoMain".format(urllib.parse.quote("admin"), urllib.parse.quote("*{-4s#aG*_>2"))
    cap = cv2.VideoCapture(url)

    _, previous_image = cap.read()

    while cap.isOpened():
        try:
            ret, frame = cap.read()

            cv2.imshow('Video', frame)
            diff = diff_without_resize(previous_image, frame)
            cv2.imshow('Diff', diff)
            diff = resize(diff)
            cv2.imshow('CNN', diff)

            thread = threading.Thread(target=detect_movement, args=(diff,))
            thread.daemon = True
            thread.start()

            previous_image = frame

            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)

    cap.release()
    cv2.destroyAllWindows()

show_video()

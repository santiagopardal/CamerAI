import cv2
import numpy as np
import threading
from CNNs import create_model
from Constants import MOVEMENT_SENSITIVITY
from YOLO import YOLOv4Tiny
import Constants

model = create_model()
model.load_weights("Neural Network/v4.8.3/model_weights")


def look_for_people(frame):
    yolo = YOLOv4Tiny()

    if yolo.there_is("person", frame):
        print("Person")
    else:
        print("No person")

    del yolo


def detect_movement(previous_frame, frame):
    previous_frame = cv2.resize(previous_frame, (256, 144), interpolation=cv2.INTER_AREA)
    previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_RGB2GRAY)

    img = cv2.resize(frame, (256, 144), interpolation=cv2.INTER_AREA)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    diff = cv2.absdiff(previous_frame, img)
    diff = np.array(diff / 255, dtype="float32")

    images = np.array([diff]).reshape((256, 144, 1))

    movement = model.predict(np.array([images]))

    if movement[0][0] >= MOVEMENT_SENSITIVITY:
        print(movement)

        look_for_people(frame)


def show_video():
    cap = cv2.VideoCapture("rtsp://{}:{}@192.168.1.131:1113/videoMain".format(Constants.USER, Constants.PASSWORD))

    _, previous_frame = cap.read()

    while cap.isOpened():
        try:
            ret, frame = cap.read()

            if previous_frame is not None and frame is not None:
                thread = threading.Thread(target=detect_movement, args=(previous_frame, frame,))
                thread.daemon = True
                thread.start()

                cv2.imshow('frame', frame)

            previous_frame = frame

            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)

    cap.release()
    cv2.destroyAllWindows()


show_video()

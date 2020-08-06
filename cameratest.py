import cv2
import numpy as np
import datetime
from time import perf_counter
import threading
from CNNs import create_model
from Constants import MOVEMENT_SENSITIVITY

model = create_model()
model.load_weights("Neural Network/v2/model_weights")


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
        cv2.imwrite("./images/{}.jpeg".format(datetime.datetime.now().time()), frame)


def show_video():
    cap = cv2.VideoCapture("rtsp://admin:maxi7500@192.168.1.131:1113/videoMain")

    _, previous_frame = cap.read()

    while(cap.isOpened()):
        try:
            ret, frame = cap.read()

            if previous_frame is not None:

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
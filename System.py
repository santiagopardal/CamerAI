import pickle
import os
import time
import threading
import GoogleAPI
import datetime
from Camera import Camera
import cv2
import argparse
import Constants
import imutils


def delete_file(path: str):
    thread = threading.Thread(target=os.remove, args=(path, ))
    thread.daemon = False
    thread.start()


def check_movement_in_batch(path: str):
    print("Cleaning on {} started at {}:{}".format(path, datetime.datetime.now().hour, datetime.datetime.now().minute))
    if os.path.exists(path + ".DS_Store"):
        os.remove(path + ".DS_Store")

    path_sorted = sorted(os.listdir(path))

    if len(path_sorted) > 0:
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video", help=path + path_sorted[0])
        ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
        args = vars(ap.parse_args())

        last_image = cv2.imread(path + "/" + path_sorted[0])
        last_image = cv2.cvtColor(last_image, cv2.COLOR_BGR2GRAY)

        movements = []
        contours_cache = []

        movements.append(path_sorted[0])

        for image in path_sorted:
            if image != movements[0] and image != ".DS_Store":
                try:
                    frame = cv2.imread(path + "/" + image)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    frame_delta = cv2.absdiff(last_image, frame)

                    threshold = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

                    threshold = cv2.dilate(threshold, None, iterations=1)
                    contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    contours = imutils.grab_contours(contours)

                    for contour in contours:
                        if not cv2.contourArea(contour) < args["min_area"]:
                            (x, y, w, h) = cv2.boundingRect(contour)

                            already_cached = False

                            for (ex, why, width, height) in contours_cache:
                                if (abs(ex - x) < 2 and abs(why - y) < 5) or (abs(ex - x) < 5 and abs(why - y) < 2):
                                    if abs(width - w) < 5 or abs(height - h) < 5:
                                        contours_cache.append((x, y, w, h))
                                        already_cached = True
                                        break

                            if w > 50 and h > 50 and not already_cached:
                                contours_cache.append((x, y, w, h))
                                if image not in movements:
                                    movements.append(image)
                                    last_image = frame

                    if image not in movements:
                        delete_file(path + "/" + image)
                        #os.remove(path + "/" + image)
                except Exception as e:
                    print("Error checking movement on image {}, error is: {}".format(image, e))

        print("Cleaning on {} finished at {}:{}".format(path, datetime.datetime.now().hour, datetime.datetime.now().minute))


class System:
    def __init__(self):
        self.last_upload = -4
        self.last_image = None
        if os.path.exists("cameras.pickle"):
            with open("cameras.pickle", "rb") as pck:
                self.cameras = pickle.load(pck)
                pck.close()
        else:
            self.cameras = []
            with open("cameras.pickle", "wb") as pck:
                pickle.dump(self.cameras, pck)
                pck.close()

    def add_camera(self, camera: Camera):
        can_insert = True
        i = 0
        while can_insert and i < len(self.cameras):
            can_insert = self.cameras[i].get_place() != camera.get_place()
            i += 1

        if can_insert:
            self.cameras.append(camera)
#            with open("cameras.pickle", "wb") as pck:
#                pickle.dump(self.cameras, pck)
#                pck.close()

    def remove_camera(self, camera: Camera):
        self.cameras.remove(camera)
        with open("cameras.pickle", "wb") as pck:
            pickle.dump(self.cameras, pck)
            pck.close()

    def run(self):
        for camera in self.cameras:
            camera.record()

        while True:
            print("Sleeping...")
         #   if datetime.datetime.now().hour % 2 == 0 and self.last_upload != datetime.datetime.now().hour:
         #       self.last_upload = datetime.datetime.now().hour
         #       self.__upload_time()

            time.sleep(Constants.UPDATE_EVERY_SECONDS)

    def __upload_time(self):
        print("Upload time!")

        if not os.path.exists("to upload"):
            os.mkdir("to upload")

        for camera in self.cameras:
            if not os.path.exists("to upload/" + camera.place):
                os.mkdir("to upload/" + camera.place)

            thread = threading.Thread(target=self.__upload, args=(camera.place,))
            thread.daemon = True
            thread.start()

    def __upload(self, path: str):
        api = GoogleAPI.GoogleAPI()

        for folder in os.listdir(path):

            if not os.path.isfile(folder):

                if not os.path.exists("to upload/" + path + "/" + folder):
                    os.mkdir("to upload/" + path + "/" + folder)

                files_list = sorted(os.listdir(path + "/" + folder))

                for i in range(len(files_list) - 4):
                    pth = path + "/" + folder + "/" + files_list[i]
                    os.rename(pth, "to upload/" + pth)

        for folder in os.listdir("to upload/" + path):

            if not os.path.isfile("to upload/" + path + "/" + folder):
                check_movement_in_batch("to upload/" + path + "/" + folder)

                for file in os.listdir("to upload/" + path + "/" + folder):

                    if str(file).endswith(".jpeg"):
                        filepath = "to upload/" + path + "/" + folder + "/"
                        uploaded = False
                        intents = 0
                        while not uploaded and intents < 10:
                            try:
                                api.upload(filepath, file, "image/jpeg")
                                os.remove(filepath + file)
                                uploaded = True
                            except Exception as e:
                                print("Error uploading:\n" + str(e))
                                intents = intents + 1
                    time.sleep(0.0001)

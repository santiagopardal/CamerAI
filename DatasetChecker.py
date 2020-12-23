import pickle
import os
import cv2
import CNNs
import numpy as np

movement_seen = []
no_movement_seen = []

if os.path.exists("movement_seen.pck"):
    with open("movement_seen.pck", "rb") as handle:
        movement_seen = pickle.load(handle)

if os.path.exists("no_movement_seen.pck"):
    with open("no_movement_seen.pck", "rb") as handle:
        no_movement_seen = pickle.load(handle)

def check_movement_folder(path):
    all_files = sorted(os.listdir(path))
    i = 0
    while i < len(all_files):
        file = all_files[i]
        if not os.path.join(path, file) in movement_seen:
            file_path = os.path.join(path, file)

            files = []
            with open(file_path, "rb") as handle:
                files = pickle.load(handle)

            a = cv2.imread(files[0], cv2.IMREAD_GRAYSCALE)
            b = cv2.imread(files[1], cv2.IMREAD_GRAYSCALE)

            diff = cv2.absdiff(a, b)
          #  d = cv2.resize(diff, (256, 144), interpolation=cv2.INTER_AREA)
          #  d = np.array(d/255, dtype="float32")

            #images = np.array([d]).reshape((256, 144, 1))

         #   movement = model.predict_on_batch(np.array([images]))

            print(file_path.replace("Movement", "No Movement").replace(file,
                                                                       "{}-fromMovement.pck".format(
                                                                           file.replace(".pck", ""))))

           # if movement[0][0] < 0.9:
          #      print(movement[0][0])
            cv2.imshow("dik", a)
            cv2.imshow("iwn", diff)
            var = cv2.waitKey(0)
            if var == ord('m'):
                j = 0
                while os.path.exists(file_path.replace("Movement", "No Movement").replace(file,
                                            "{}-fromMovement.pck".format(j))):
                    j += 100
                os.rename(file_path,
                          file_path.replace("Movement", "No Movement").replace(file,
                                            "{}-fromMovement.pck".format(j)))

                i += 1
            elif var == ord('b'):
                print("Going back")
                i = i - 1
            else:
                i += 1
        else:
            i += 1

def check_no_movement_folder(path):
    all_files = sorted(os.listdir(path))
    i = 3500
    while i < len(all_files):
        file = all_files[i]
        if not os.path.join(path, file) in no_movement_seen:
            if file.endswith("fromMovement.pck"):
                file_path = os.path.join(path, file)

                files = []
                print(file)
                with open(file_path, "rb") as handle:
                    files = pickle.load(handle)

                a = cv2.imread(files[0], cv2.IMREAD_GRAYSCALE)
                b = cv2.imread(files[1], cv2.IMREAD_GRAYSCALE)

                diff = cv2.absdiff(a, b)

                print(file_path.replace("No Movement", "Movement").replace(file,
                                                                           "{}-fromNoMovement.pck".format(
                                                                               file.replace(".pck", ""))))
                cv2.imshow("iwn", diff)

                var = cv2.waitKey(0)

                if var == ord('m'):
                    os.rename(file_path,
                              file_path.replace("No Movement", "Movement").replace(file,
                                                "{}-fromNoMovement.pck".format(file.replace(".pck", ""))))
                    i += 1
                elif var == ord('b'):
                    i = i-1
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1

def mark_all_as_seen(path, name):
    seen = []

    for place in os.listdir(path):
        pth = os.path.join(path, place)

        for file in os.listdir(pth):
            file_path = os.path.join(pth, file)
            seen.append(file_path)

    with open(name, "wb") as handle:
        pickle.dump(seen, handle)


check_no_movement_folder("No Movement\\list\\Back Yard")
#mark_all_as_seen("Movement\\list\\", "movement_seen.pck")
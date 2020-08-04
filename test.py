from GoogleAPI import GoogleAPI
from System import System
from System import check_movement_in_batch
from Camera import FI9803PV3, FI89182
import threading
"""
t1 = threading.Thread(target=check_movement_in_batch, args=("Front Yard/2020-08-02",))
t2 = threading.Thread(target=check_movement_in_batch, args=("Front Yard 2/2020-08-02",))
t3 = threading.Thread(target=check_movement_in_batch, args=("Back Yard/2020-08-02",))
t4 = threading.Thread(target=check_movement_in_batch, args=("Back Yard 2/2020-08-02",))

t1.daemon = False
t2.daemon = False
t3.daemon = False
t4.daemon = False

t1.start()
t2.start()
t3.start()
t4.start()
"""

sys = System()
#api = GoogleAPI()
#system = System()
sys.add_camera(FI9803PV3("192.168.1.131", 1111, "Front Yard", "admin", "maxi7500"))
sys.add_camera(FI89182("192.168.1.133", 2222, "Front Yard 2", "admin", "maxi7500"))
sys.add_camera(FI9803PV3("192.168.1.132", 4444, "Back Yard", "admin", "maxi7500"))
sys.add_camera(FI9803PV3("192.168.1.130", 3333, "Back Yard 2", "admin", "maxi7500"))
sys.run()

"""
def check_movement_in_batch(path):
    if os.path.exists(path + ".DS_Store"):
        os.remove(path + ".DS_Store")

    path_sorted = sorted(os.listdir(path))

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help=path + path_sorted[0])
    ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
    args = vars(ap.parse_args())

    first_frame = cv2.imread(path + "/" + path_sorted[0])
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    movements = []
    contours_cache = []

    movements.append(path_sorted[0])

    for image in path_sorted:
        if image != movements[0] and image != ".DS_Store":
            try:
                second_frame = cv2.imread(path + "/" + image)
                second_frame = cv2.cvtColor(second_frame, cv2.COLOR_BGR2GRAY)

                frame_delta = cv2.absdiff(first_frame, second_frame)

                threshold = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

                threshold = cv2.dilate(threshold, None, iterations=0)
                contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)

                for contour in contours:
                    if not cv2.contourArea(contour) < args["min_area"]:
                        (x, y, w, h) = cv2.boundingRect(contour)
                        cv2.rectangle(second_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                        already_cached = False

                        for (ex, why, width, height) in contours_cache:
                            if abs(ex - x) < 2 and abs(why - y) < 2:
                                if abs(width - w) < 5 or abs(height - h) < 5:
                                    contours_cache.append((x, y, w, h))
                                    already_cached = True
                                    break

                        if w > 50 and h > 50 and not already_cached:
                            contours_cache.append((x, y, w, h))
                            if image not in movements:
                                movements.append(image)
                              #  first_frame = second_frame
                print(image)
                if image in movements:
                    cv2.waitKey(0)
                    cv2.imshow("image", second_frame)
            except Exception:
                pass
    print(len(movements))
    cv2.destroyAllWindows()


check_movement_in_batch("Front Yard/2020-01-15")
"""
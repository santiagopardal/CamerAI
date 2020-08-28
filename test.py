from GoogleAPI import GoogleAPI
from System import System
from Camera import FI9803PV3, FI89182
import threading
import time
from YOLO import YOLOv4Tiny
import Constants
import cv2

sys = System()
sys.add_camera(FI9803PV3("192.168.1.131", 1111, "Front Yard", Constants.USER, Constants.PASSWORD))
sys.add_camera(FI89182("192.168.1.133", 2222, "Front Yard 2", Constants.USER, Constants.PASSWORD))
sys.add_camera(FI9803PV3("192.168.1.132", 4444, "Back Yard", Constants.USER, Constants.PASSWORD))
sys.add_camera(FI9803PV3("192.168.1.130", 3333, "Back Yard 2", Constants.USER, Constants.PASSWORD))
sys.run()
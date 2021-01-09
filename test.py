from System import System
from Cameras.Camera import FI9803PV3, FI89182
import Constants
from Observations.Observers import Observer

sys = System()
sys.add_camera(FI9803PV3("192.168.1.131", 1111, "Front Yard", Constants.USER, Constants.PASSWORD, motion_handlers=[], observer=Observer()))
sys.add_camera(FI89182("192.168.1.133", 2222, "Front Yard 2", Constants.USER, Constants.PASSWORD, motion_handlers=[], observer=Observer()))
sys.add_camera(FI9803PV3("192.168.1.132", 4444, "Back Yard", Constants.USER, Constants.PASSWORD, motion_handlers=[], observer=Observer()))
sys.add_camera(FI9803PV3("192.168.1.130", 3333, "Back Yard 2", Constants.USER, Constants.PASSWORD, motion_handlers=[], observer=Observer()))
sys.run_with_gui()

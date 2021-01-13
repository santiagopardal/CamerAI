from System import System
from Cameras.Camera import FI9803PV3, FI89182
import Constants
from Handlers.Handler import FrameHandler


sys = System()

cameras = [
    FI9803PV3("192.168.1.131", 1111, 1113, "Front Yard", Constants.USER, Constants.PASSWORD),
    FI89182("192.168.1.133", 2222, "Front Yard 2", Constants.USER, Constants.PASSWORD),
    FI9803PV3("192.168.1.132", 4444, 4446, "Back Yard", Constants.USER, Constants.PASSWORD),
    FI9803PV3("192.168.1.130", 3333, 3335, "Back Yard 2", Constants.USER, Constants.PASSWORD)
]

for camera in cameras:
    fh = FrameHandler(camera)
    camera.set_frames_handler(fh)
    sys.add_camera(camera)

sys.run_with_gui()

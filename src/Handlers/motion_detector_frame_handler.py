from src import constants
from src.Observations.Observers.lite_observer import LiteObserver
from src.Handlers.frame_handler import FrameHandler
from src.Handlers.buffered_motion_handler import BufferedMotionHandler


class MotionDetectorFrameHandler(FrameHandler):
    def __init__(self, camera):
        super().__init__(LiteObserver(), [BufferedMotionHandler(camera, constants.SECONDS_TO_BUFFER)])

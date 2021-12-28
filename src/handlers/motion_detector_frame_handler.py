from src import constants
from src.observations.observers.lite_observer import LiteObserver
from src.handlers.frame_handler import FrameHandler
from src.handlers.buffered_motion_handler import BufferedMotionHandler


class MotionDetectorFrameHandler(FrameHandler):
    def __init__(self, camera):
        super().__init__(LiteObserver(), [BufferedMotionHandler(camera, constants.SECONDS_TO_BUFFER)])

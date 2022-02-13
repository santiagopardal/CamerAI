from src import constants
from src.observations.observers.dynamic_movement_detection_observer import DynamicMovementDetectionObserver
from src.handlers.frame_handler import FrameHandler
from src.handlers.buffered_motion_handler import BufferedMotionHandler


class MotionDetectorFrameHandler(FrameHandler):
    def __init__(self, camera):
        super().__init__(DynamicMovementDetectionObserver(), [BufferedMotionHandler(camera, constants.SECONDS_TO_BUFFER)])

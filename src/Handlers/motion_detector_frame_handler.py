from src import constants
from src.Observations.Observers.lite_observer import LiteObserver
from src.Handlers.frame_handler import FrameHandler
from src.Handlers.asynchronous_disk_store_motion_handler import AsynchronousDiskStoreMotionHandler


class MotionDetectorFrameHandler(FrameHandler):
    def __init__(self, camera):
        super().__init__(LiteObserver(), [AsynchronousDiskStoreMotionHandler(camera.place,
                                                                             constants.VIDEO_BUFFERS_SIZE,
                                                                             camera.framerate)])

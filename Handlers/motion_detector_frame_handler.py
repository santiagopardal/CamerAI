from Observations.Observers.lite_observer import LiteObserver
from Handlers.frame_handler import FrameHandler
from Handlers.asynchronous_disk_store_motion_handler import AsynchronousDiskStoreMotionHandler


class MotionDetectorFrameHandler(FrameHandler):
    def __init__(self, camera):
        super().__init__(LiteObserver(), [AsynchronousDiskStoreMotionHandler(camera.place, 30)])

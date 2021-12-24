from collections import deque
from src.Handlers.motion_handler import MotionHandler
from src.Frames.Savers.frame_saver import FrameSaver
from src.Frames.Savers.local_frame_saver import LocalFrameSaver


class SynchronousDiskStoreMotionHandler(MotionHandler):
    """
    Handles motion storing the frames on disk synchronously.
    """

    def __init__(self, storing_path: str, frame_saver: FrameSaver = None):
        """
        Initializes the handler.
        :param storing_path: Folder name to which store the frames.
        """
        self._frames = deque()
        self._storing_path = storing_path
        self._frame_saver = frame_saver if frame_saver else LocalFrameSaver(storing_path)

        super().__init__()

    def handle(self, event: list):
        """
        Receives the frames and stores them straightaway.
        :param event: List of frames in which there has been movement.
        """
        for frame in event:
            self._frame_saver.save(frame)

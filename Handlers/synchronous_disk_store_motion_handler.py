from collections import deque
from Handlers.motion_handler import MotionHandler


class SynchronousDiskStoreMotionHandler(MotionHandler):
    """
    Handles motion storing the frames on disk synchronously.
    """

    def __init__(self, storing_path: str):
        """
        Initializes the handler.
        :param storing_path: Folder name to which store the frames.
        """
        self._frames = deque()

        self._storing_path = storing_path

        super().__init__()

    def handle(self, event: list):
        """
        Receives the frames and stores them straightaway.
        :param event: List of frames in which there has been movement.
        """
        for frame in event:
            frame.store(self._storing_path)
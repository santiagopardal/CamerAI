from src.handlers.motion_handler import MotionHandler
from collections import deque
import os
from src.constants import STORING_PATH
import src.api.temporal_videos as temporal_videos_api
from src.media.savers.media_saver import MediaSaver
from src.media.savers.local_video_saver import LocalVideoSaver
from src.media.savers.remote_video_saver import RemoteVideoSaver


class BufferedMotionHandler(MotionHandler):
    """
    Handles motion storing the frames on disk asynchronously.
    """
    def __init__(self, camera, seconds_to_buffer: int = 2, media_saver: MediaSaver = None):
        """
        Initializes the handler.
        :param seconds_to_buffer: If set, the frames will be stored as soon as the buffer reaches this number of frames,
        if not set, the frames will be stored as soon as they arrive to the handler.
        """
        self._frames = deque()
        self._frames.append([])
        self._camera = camera
        self._storing_path = os.path.join(STORING_PATH, camera.place)
        self._media_saver = media_saver if media_saver else RemoteVideoSaver(camera.id, self._storing_path, camera.frame_rate)#LocalVideoSaver(self._storing_path, camera.frame_rate)
        self._buffer_size = seconds_to_buffer*camera.frame_rate

        super().__init__()

    def handle(self, event: list):
        """
        Receives the frames and once the handler is ready stores them.
        :param event: List of frames in which there has been movement.
        """
        if event:
            self._frames[0] = self._frames[0] + event

            if len(self._frames[0]) >= self._buffer_size:
                to_store = self._frames.popleft()
                self._frames.append([])
                self._media_saver.save(to_store)

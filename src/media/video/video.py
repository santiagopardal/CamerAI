from cv2 import VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FPS
import src.api.temporal_videos as temporal_videos_api
import asyncio


class Video:
    _video: VideoCapture

    def __init__(self, id: int, path: str):
        self._id = id
        self._path = path

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self._video.read()

        if ret:
            return frame
        else:
            self._video.release()
            raise StopIteration

    @property
    def width(self):
        return int(self._video.get(CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self._video.get(CAP_PROP_FRAME_HEIGHT))

    @property
    def frame_rate(self):
        return self._video.get(CAP_PROP_FPS)

    def delete(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(temporal_videos_api.remove_video(self._id))

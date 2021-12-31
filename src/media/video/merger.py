from cv2 import VideoWriter, VideoWriter_fourcc


class VideoMerger:
    def __init__(self, videos: list):
        self._videos = videos
        self._frame_rate = videos[0].frame_rate
        self._height = videos[0].height
        self._width = videos[0].width

    def merge(self, path: str):
        fourcc = VideoWriter_fourcc(*'mp4v')
        writer = VideoWriter(path, fourcc, self._frame_rate, (self._width, self._height))

        for video in self._videos:
            for frame in video:
                writer.write(frame)
            video.delete()

        writer.release()

from src.media.video.video import Video
from src.media.video.local_video import LocalVideo
from src.media.video.remote_video import RemoteVideo
from src.constants import API_URL


def create(video: dict) -> Video:
    if video['locally_stored']:
        endpoint = '{}/temporal_videos/{}/stream'.format(API_URL, video['id'])
        return RemoteVideo(video['id'], video['path'], endpoint)
    else:
        return LocalVideo(video['id'], video['path'])

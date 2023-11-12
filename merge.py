from datetime import datetime, timedelta
import src.api.temporal_videos as temporal_videos_api
from src.utils.date_utils import get_numbers_as_string
import src.api.api as API
import src.api.videos as videos_api
from src.api.cameras import get_cameras
import os
from src.constants import STORING_PATH
from libs.VideosMerger import VideoMerger, VideosIterator
import src.media.video.video_factory as video_factory
import json
from socket import socket, AF_INET, SOCK_STREAM


def merge_cameras_video(camera: dict, date: datetime):
    temporal_videos = temporal_videos_api.get_temporal_videos(camera['id'], date)

    if temporal_videos:
        pth = os.path.join(STORING_PATH, camera['name'])

        day, month, year = get_numbers_as_string(date)
        video_path = "{}/{}-{}-{}.mp4".format(pth, year, month, day)

        videos = VideosIterator(temporal_videos, video_factory)
        merger = VideoMerger(videos)
        merger.merge(video_path, True)

        videos_api.register_new_video(camera['id'], date, video_path)


def get_my_id():
    sock: socket = socket(AF_INET, SOCK_STREAM)
    sock.connect(('127.0.0.1', LISTENING_PORT))
    request = pack_message(NODE_REQUEST, json.dumps({"method": "id"}))
    sock.send(request)
    sock.recv(1)
    content_length = int.from_bytes(sock.recv(8), 'little')
    response = json.loads(sock.recv(content_length))
    sock.close()
    return response['result']


def transform_yesterday_into_video():
    yesterday = datetime.now() - timedelta(days=1)
    node_id = get_my_id()
    API.set_headers({"node_id": str(node_id)})
    video_factory.NODE_ID = node_id
    cameras = get_cameras(node_id)

    for camera in cameras:
        try:
            merge_cameras_video(camera, yesterday)
        except Exception as e:
            print("Error merging videos:", e)


if __name__ == '__main__':
    transform_yesterday_into_video()

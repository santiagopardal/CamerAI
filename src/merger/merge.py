from datetime import datetime, timedelta
import src.api.temporal_videos as temporal_videos_api
from src.utils.date_utils import get_numbers_as_string
import src.api.videos as videos_api
from src.api.cameras import get_cameras
import os
from src.constants import STORING_PATH
from libs.VideosMerger.videos_iterator import VideosIterator
from libs.VideosMerger.merger import VideoMerger
import src.media.video.video_factory as video_factory
import asyncio


async def merge_cameras_video(camera: dict, date: datetime):
    temporal_videos = await temporal_videos_api.get_temporal_videos(camera['id'], date)

    if temporal_videos:
        pth = os.path.join(STORING_PATH, camera['name'])

        day, month, year = get_numbers_as_string(date)
        video_path = "{}/{}-{}-{}.mp4".format(pth, year, month, day)

        videos = VideosIterator(temporal_videos, video_factory)
        merger = VideoMerger(videos)
        merger.merge(video_path, True)

        asyncio.create_task(videos_api.register_new_video(camera['id'], date, video_path))


async def transform_yesterday_into_video():
    yesterday = datetime.now() - timedelta(days=1)
    cameras = await get_cameras()

    for camera in cameras:
        try:
            await merge_cameras_video(camera, yesterday)
        except Exception as e:
            print("Error merging videos:", e)


if __name__ == '__main__':
    asyncio.run(transform_yesterday_into_video())

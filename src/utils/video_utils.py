import cv2


def append_to_video(to: cv2.VideoWriter, to_append_path: str):
    try:
        video = cv2.VideoCapture(to_append_path)
        r = True

        while video.isOpened() and r:
            r, frame = video.read()
            if r:
                to.write(frame)
    except Exception:
        pass


def get_video_properties(video_path: str):
    video = cv2.VideoCapture(video_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = video.get(cv2.CAP_PROP_FPS)

    return width, height, frame_rate


def create_video_writer(video_path, width, height, frame_rate):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    return cv2.VideoWriter(video_path, fourcc, frame_rate, (width, height))

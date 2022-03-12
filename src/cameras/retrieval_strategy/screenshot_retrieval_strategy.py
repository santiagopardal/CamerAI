from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
import cv2
from numpy import ndarray
import requests
import numpy as np


class ScreenshotRetrievalStrategy(RetrievalStrategy):

    def __init__(self, url: str, frame_rate: int, frame_width: int, frame_height: int):
        self._url = url
        self._frame_rate = frame_rate
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._live_video = None

    def retrieve(self) -> ndarray:
        response = requests.get(self._url, stream=True).raw
        frame = np.asarray(bytearray(response.read()), dtype="uint8")
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)

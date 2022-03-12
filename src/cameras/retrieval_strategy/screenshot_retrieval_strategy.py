from src.cameras.retrieval_strategy.retrieval_strategy import RetrievalStrategy
import cv2
from numpy import ndarray
import requests
import numpy as np


class ScreenshotRetrievalStrategy(RetrievalStrategy):

    def __init__(self, url: str):
        self._url = url

    def retrieve(self) -> ndarray:
        response = requests.get(self._url, stream=True).raw
        frame = np.asarray(bytearray(response.read()), dtype="uint8")
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)

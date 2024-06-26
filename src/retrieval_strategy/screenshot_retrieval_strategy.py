from src.retrieval_strategy.retrieval_strategy import RetrievalStrategy
import cv2
from numpy import ndarray
import requests
import numpy as np


class ScreenshotRetrievalStrategy(RetrievalStrategy):

    def retrieve(self) -> ndarray:
        response = requests.get(self._camera.snapshot_url, stream=True).raw
        frame = np.asarray(bytearray(response.read()), dtype="uint8")
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)

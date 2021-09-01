from src.Observations.Observers.observer import Observer
from src.Observations.Models.V3ModelMotionDetector import V3MotionDetector


class MovementDetectionObserver(Observer):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        super().__init__(V3MotionDetector())

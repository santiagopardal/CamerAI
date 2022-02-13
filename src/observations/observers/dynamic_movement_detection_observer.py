from src.observations.observers.observer import Observer
from src.observations.models.factory import create_model


class DynamicMovementDetectionObserver(Observer):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        model = create_model()
        super().__init__(model)

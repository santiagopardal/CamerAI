from src.observations.observers.observer import Observer
import src.observations.models.factory as model_factory


class DynamicMovementDetectionObserver(Observer):
    def __init__(self):
        model = model_factory.create_model()
        super().__init__(model)

from numpy import ndarray


class Model:
    def __init__(self):
        pass

    def predict(self, data: ndarray) -> float:
        pass

    def predict_on_batch(self, data: list[ndarray]) -> list[float]:
        pass

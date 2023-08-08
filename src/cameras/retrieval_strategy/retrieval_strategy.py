from numpy import ndarray


class RetrievalStrategy:
    def connect(self):
        pass

    def retrieve(self) -> ndarray:
        pass

    def disconnect(self):
        pass

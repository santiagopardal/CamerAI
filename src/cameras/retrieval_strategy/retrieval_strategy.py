from numpy import ndarray


class RetrievalStrategy:
    async def connect(self):
        pass

    async def retrieve(self) -> ndarray:
        pass

    async def disconnect(self):
        pass

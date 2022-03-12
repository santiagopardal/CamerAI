class RetrievalStrategy:
    def connect(self):
        """
        Connects to the camera.
        """
        pass

    def retrieve(self):
        """
        Retrieves a frame from the camera
        """
        pass

    def disconnect(self):
        """
        Releases everything related to the connection
        """
        pass

class ObservationStrategy:
    def __init__(self, observer):
        self._observer = observer

    def observe(self, frames: list) -> list:
        """
        Receives a list of frames and determines those in which there has been movement.
        :param frames: Frames to analyse.
        """
        pass

    def frames_to_buffer(self) -> int:
        """
        Returns the number of frames to buffer.
        """
        pass

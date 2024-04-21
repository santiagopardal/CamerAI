
CONFIGURATIONS_KEYS = ["sensitivity", "recording"]


class Configurations:
    _sensitivity: float
    recording: bool

    def __init__(self, **configurations):
        self._sensitivity = configurations["sensitivity"]
        self.recording = configurations["recording"]

    @property
    def sensitivity(self) -> float:
        return self._sensitivity

    @sensitivity.setter
    def sensitivity(self, sensitivity: float):
        if sensitivity < 0 or sensitivity > 1:
            raise Exception("Sensitivity must be a number between 0 and 1")

        self._sensitivity = sensitivity

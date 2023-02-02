
CONFIGURATIONS_KEYS = ["sensitivity", "recording"]


class Configurations:
    _sensitivity: int
    recording: bool

    def __init__(self, **configurations):
        self._sensitivity = configurations["sensitivity"]
        self.recording = configurations["recording"]

    @property
    def sensitivity(self) -> int:
        return self._sensitivity

    @sensitivity.setter
    def sensitivity(self, sensitivity: int):
        if sensitivity < 0 or sensitivity > 1:
            raise Exception("Sensitivity must be a number between 0 and 1")

        self._sensitivity = sensitivity

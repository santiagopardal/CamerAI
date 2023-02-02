class Properties:
    _id: int
    name: str
    ip: str
    _port: int
    _streaming_port: int
    _frame_width: int
    _frame_height: int
    _frame_rate: int

    def __init__(self, **properties):
        self._id = properties["id"]
        self.name = properties["name"]
        self.ip = properties["ip"]
        self._port = properties["http_port"]
        self._streaming_port = properties["streaming_port"]
        self._frame_width = properties["frame_width"]
        self._frame_height = properties["frame_height"]
        self._frame_rate = properties["frame_rate"]

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int):
        if id <= 0:
            raise Exception('The ID must be greater than 0')

        self._id = id

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, port: int):
        if port <= 0 or port > 65535:
            raise Exception('The port number must be a number between 0 and 65535')

        self._port = port

    @property
    def streaming_port(self) -> int:
        return self._port

    @streaming_port.setter
    def streaming_port(self, streaming_port: int):
        if streaming_port is not None:
            if streaming_port <= 0 or streaming_port > 65535:
                raise Exception('The streaming_port number must be a number between 0 and 65535')

            self._streaming_port = streaming_port

    @property
    def frame_width(self) -> int:
        return self._frame_width

    @frame_width.setter
    def frame_width(self, frame_width: int):
        if frame_width <= 0:
            raise Exception('The frame width must be greater than 0')

        self._frame_width = frame_width

    @property
    def frame_height(self) -> int:
        return self._frame_height

    @frame_height.setter
    def frame_height(self, frame_height: int):
        if frame_height <= 0:
            raise Exception('The frame height must be greater than 0')

        self._frame_height = frame_height

    @property
    def frame_rate(self) -> int:
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, frame_rate: int):
        if frame_rate <= 0:
            raise Exception('The frame rate must be greater than 0')

        self._frame_rate = frame_rate

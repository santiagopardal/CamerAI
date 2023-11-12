from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateSensitivityRequest(_message.Message):
    __slots__ = ["camera_id", "sensitivity"]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    camera_id: int
    sensitivity: float
    def __init__(self, camera_id: _Optional[int] = ..., sensitivity: _Optional[float] = ...) -> None: ...

class CameraIdParameterRequest(_message.Message):
    __slots__ = ["camera_id"]
    CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    camera_id: int
    def __init__(self, camera_id: _Optional[int] = ...) -> None: ...

class SwitchRecordingRequest(_message.Message):
    __slots__ = ["cameras_ids"]
    CAMERAS_IDS_FIELD_NUMBER: _ClassVar[int]
    cameras_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, cameras_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class CameraInfo(_message.Message):
    __slots__ = ["id", "name", "ip", "http_port", "streaming_port", "frame_width", "frame_height", "frame_rate", "user", "password", "model", "configurations"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    HTTP_PORT_FIELD_NUMBER: _ClassVar[int]
    STREAMING_PORT_FIELD_NUMBER: _ClassVar[int]
    FRAME_WIDTH_FIELD_NUMBER: _ClassVar[int]
    FRAME_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_RATE_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    ip: str
    http_port: int
    streaming_port: int
    frame_width: int
    frame_height: int
    frame_rate: int
    user: str
    password: str
    model: str
    configurations: CameraConfigurations
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., ip: _Optional[str] = ..., http_port: _Optional[int] = ..., streaming_port: _Optional[int] = ..., frame_width: _Optional[int] = ..., frame_height: _Optional[int] = ..., frame_rate: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., model: _Optional[str] = ..., configurations: _Optional[_Union[CameraConfigurations, _Mapping]] = ...) -> None: ...

class CameraConfigurations(_message.Message):
    __slots__ = ["sensitivity", "recording"]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    RECORDING_FIELD_NUMBER: _ClassVar[int]
    sensitivity: float
    recording: bool
    def __init__(self, sensitivity: _Optional[float] = ..., recording: bool = ...) -> None: ...

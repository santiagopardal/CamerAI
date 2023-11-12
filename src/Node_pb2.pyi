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

class ManyCameraIdsRequest(_message.Message):
    __slots__ = ["cameras_ids"]
    CAMERAS_IDS_FIELD_NUMBER: _ClassVar[int]
    cameras_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, cameras_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class CameraInfo(_message.Message):
    __slots__ = ["id", "name", "model", "ip", "streaming_port", "http_port", "user", "password", "width", "height", "framerate", "configurations"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    STREAMING_PORT_FIELD_NUMBER: _ClassVar[int]
    HTTP_PORT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAMERATE_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    model: str
    ip: str
    streaming_port: int
    http_port: int
    user: str
    password: str
    width: int
    height: int
    framerate: int
    configurations: CameraConfigurations
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., model: _Optional[str] = ..., ip: _Optional[str] = ..., streaming_port: _Optional[int] = ..., http_port: _Optional[int] = ..., user: _Optional[str] = ..., password: _Optional[str] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., framerate: _Optional[int] = ..., configurations: _Optional[_Union[CameraConfigurations, _Mapping]] = ...) -> None: ...

class CameraConfigurations(_message.Message):
    __slots__ = ["sensitivity", "recording"]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    RECORDING_FIELD_NUMBER: _ClassVar[int]
    sensitivity: float
    recording: bool
    def __init__(self, sensitivity: _Optional[float] = ..., recording: bool = ...) -> None: ...

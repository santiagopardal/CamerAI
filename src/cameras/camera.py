import enum
import urllib
from typing import Optional

from numpy import ndarray
from pydantic import BaseModel, field_validator, PositiveInt, Field, model_validator
from src.cameras.configurations import Configurations
import logging

from src.events_managers.events_manager import get_events_manager


SENSITIVITY_UPDATE_EVENT = "SENSITIVITY_UPDATE"
RECORDING_SWITCHED_EVENT = "RECORDING_SWITCHED_EVENT"


class LiveVideoURLs(enum.StrEnum):
    FI9803PV3 = "rtsp://{}:{}@{}:{}/videoMain"
    FI89182 = "http://{}:{}/videostream.cgi?user={}&pwd={}"


class SnapshotURLs(enum.StrEnum):
    FI9803PV3 = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"
    FI89182 = "http://{}:{}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={}&pwd={}"


class Camera(BaseModel):
    id: PositiveInt
    name: str
    model: str
    ip: str
    streaming_port: Optional[PositiveInt]
    http_port: PositiveInt
    width: PositiveInt
    height: PositiveInt
    framerate: PositiveInt
    configurations: Configurations

    video_url: Optional[str] = Field(default=None)
    snapshot_url: Optional[str] = Field(default=None)

    last_frame: Optional[ndarray] = Field(default_factory=lambda: None)

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="before")
    @classmethod
    def validate_camera(cls, data: dict) -> dict:
        user = urllib.parse.quote(data["user"])
        password = urllib.parse.quote(data["password"])
        ip = data["ip"]
        streaming_port = data["streaming_port"]
        http_port = data["http_port"]

        data["video_url"] = LiveVideoURLs[data["model"]].format(user, password, ip, streaming_port)
        data["snapshot_url"] = SnapshotURLs[data["model"]].format(ip, http_port, user, password)

        return data

    @field_validator("streaming_port", "http_port")
    @classmethod
    def validate_port(cls, port: Optional[PositiveInt]) -> Optional[PositiveInt]:
        if port is not None and not 0 <= port <= 65535:
            raise Exception('The port number must be a number between 0 and 65535')

        return port

    def update_sensitivity(self, sensitivity: float):
        old_sensitivity = self.configurations.sensitivity
        self.configurations.sensitivity = sensitivity
        get_events_manager().notify(
            event_type=SENSITIVITY_UPDATE_EVENT,
            publisher=self,
            sensitivity=sensitivity
        )
        logging.info(f"Updated sensitivity to camera with ID {self.id} from {old_sensitivity} to {sensitivity}")

    def record(self):
        if not self.configurations.recording:
            self.configurations.recording = True
            get_events_manager().notify(
                event_type=RECORDING_SWITCHED_EVENT,
                publisher=self,
                recording=True
            )

    def stop_recording(self):
        if self.configurations.recording:
            self.configurations.recording = False
            get_events_manager().notify(
                event_type=RECORDING_SWITCHED_EVENT,
                publisher=self,
                recording=False
            )

    def __eq__(self, other):
        return isinstance(other, Camera) and other.ip == self.ip and other.http_port == self.http_port

    def __hash__(self):
        return hash(f"{self.ip}:{self.http_port}@{self.name}")

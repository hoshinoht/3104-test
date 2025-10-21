from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TelemetryData(_message.Message):
    __slots__ = ("van_id", "latitude", "longitude", "speed")
    VAN_ID_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    van_id: str
    latitude: float
    longitude: float
    speed: float
    def __init__(self, van_id: _Optional[str] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., speed: _Optional[float] = ...) -> None: ...

class Alert(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

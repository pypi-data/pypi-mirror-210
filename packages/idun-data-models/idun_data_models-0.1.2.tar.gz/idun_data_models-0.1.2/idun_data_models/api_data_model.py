"""
This module defines data classes that are used by the IDUN Data API, defined with Pydantic.
"""

from datetime import datetime
from pydantic import root_validator, validator
from pydantic.dataclasses import dataclass
from .parameters import MAX_ID_LENGTH


@dataclass(frozen=True)
class Message:
    """
    A Message encapsulates encrypted device packets with metadata.
    The IDUN SDK sends Messages with device data to the IDUN Cloud through the websocket API.
    """
    recordingID: str
    deviceID: str
    deviceTimestamp: datetime
    connectionID: str | None = None
    payload: str | None = None
    impedance: float | None = None

    # DEPRECATED: these fields will be replaced by explicit API calls
    stop: bool | None = None
    "Signal that the frontend sends to stop the recording"
    recorded: bool | None = None
    "Signal that the recorder sends to signal that batch processing is complete"
    enableStreamer: bool | None = None
    "Signal that the frontend can send to disable live streaming"

    @validator("recordingID", "deviceID", "connectionID")
    def limit_length(cls, v, field):
        if v and len(v) > MAX_ID_LENGTH:
            raise ValueError(f"{field} is too long. Max length: {MAX_ID_LENGTH}")
        return v


@dataclass(frozen=True)
class DataStreams:
    "Real time data streams available to return to the client"

    bandpass_eeg: bool= False
    "Enables a stream of bandpass filtered EEG signal"
    # The following options are not yet supported
    #raw_eeg: bool = False
    #spectrogram: bool= False

    @root_validator
    def validate_streaming_modes(cls, values):
        "Forbid invalid streaming mode selection"
        return values

@dataclass(frozen=True)
class GuardianRecording:
    """
    A GuardianRecording is a contiguous data capture session of the IDUN Guardian through a specific frontend client.
    It is part of the IDUN REST API.
    """

    recordingID: str
    deviceID: str
    displayName: str
    "User-friendly name used in the UI"

    # Configuration options (should be optional)
    data_stream_subscription: DataStreams | None = None
    "Subscribe to real time data streams. No data stream by default."

    @validator("recordingID", "deviceID", "displayName")
    def limit_length(cls, v, field):
        if len(v) > MAX_ID_LENGTH:
            raise ValueError(f"{field} is too long. Max length: {MAX_ID_LENGTH}")
        return v

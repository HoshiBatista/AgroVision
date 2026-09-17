"""Pydantic v2 request/response schemas for the API."""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, EmailStr, Field, field_validator


class BoundingBoxSchema(BaseModel):
    """Bounding box in absolute pixel coordinates."""

    x1: float
    y1: float
    x2: float
    y2: float


class DetectionSchema(BaseModel):
    """A single detected object."""

    label: str
    confidence: float
    confident: bool
    box: BoundingBoxSchema


class ModelInfoSchema(BaseModel):
    """Metadata about the loaded detection model."""

    name: str
    version: str
    weights_path: str
    weights_sha256: str
    device: str
    image_size: int
    confidence_threshold: float
    classes: list[str]
    limitations: list[str]


class ModelThresholdRequest(BaseModel):
    """Runtime confidence threshold used for confident counts."""

    confidence_threshold: float = Field(ge=0.25, le=0.95)


class ImagePredictionResponse(BaseModel):
    """Result of running detection on a single image."""

    request_id: str
    model_version: str
    confidence_threshold: float
    width: int
    height: int
    count: int
    uncertain_count: int
    mean_confidence: float
    processing_ms: float
    detections: list[DetectionSchema]
    annotated_image: str = Field(description="Annotated image as a base64 data URL")


class CountSampleSchema(BaseModel):
    """A single count-over-time point."""

    timestamp_s: float
    frame_index: int
    count: int


class VideoPredictionResponse(BaseModel):
    """Result of running detection over an uploaded video."""

    request_id: str
    model_version: str
    frames_processed: int
    max_count: int
    mean_count: float
    peak_timestamp_s: float
    processing_ms: float
    annotated_video_url: str
    samples: list[CountSampleSchema]
    keyframes: list[str] = Field(
        default_factory=list, description="Annotated keyframes as base64 data URLs"
    )


class HealthResponse(BaseModel):
    """Process health."""

    status: str
    version: str


class ReadyResponse(BaseModel):
    """Model readiness."""

    ready: bool
    model_loaded: bool


class ErrorBody(BaseModel):
    """Stable error payload."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Envelope for error responses."""

    error: ErrorBody
    request_id: str


class RegisterRequest(BaseModel):
    """New-user registration payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Refresh-token payload."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Issued token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Authenticated user identity."""

    id: int
    email: str
    role: str
    created_at: datetime


class StreamSchema(BaseModel):
    """A configured drone stream."""

    id: str
    name: str
    location: str
    kind: str


class ConnectRtspStreamRequest(BaseModel):
    """A live RTSP source to attach to the running dashboard."""

    id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
    name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=160)
    uri: str = Field(min_length=8, max_length=2048)

    @field_validator("uri")
    @classmethod
    def validate_rtsp_uri(cls, value: str) -> str:
        """Allow only RTSP URLs with a hostname."""
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"rtsp", "rtsps"} or not parsed.hostname:
            raise ValueError("uri must be an rtsp:// or rtsps:// URL with a hostname")
        return value


class StreamMetricsSchema(BaseModel):
    """Latest metrics for a running stream."""

    stream_id: str
    status: str
    sheep_count: int
    mean_confidence: float
    latency_ms: float
    frame_index: int


class DashboardSnapshot(BaseModel):
    """Aggregate dashboard state across streams."""

    total_sheep: int
    active_streams: int
    streams: list[StreamMetricsSchema]


class SessionRecordSchema(BaseModel):
    """A journal entry for one inference session."""

    id: int
    kind: str
    source_name: str
    sheep_count: int
    mean_confidence: float
    model_version: str
    created_at: datetime

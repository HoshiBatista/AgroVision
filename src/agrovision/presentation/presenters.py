"""Map domain results to API response schemas."""

from __future__ import annotations

import base64

from agrovision.application.use_cases.dashboard import DashboardState
from agrovision.application.use_cases.detect_image import ImageDetectionResult
from agrovision.application.use_cases.detect_video import VideoDetectionResult
from agrovision.domain.detection import Detection
from agrovision.domain.model import ModelMetadata
from agrovision.domain.report import SessionRecord
from agrovision.domain.stream import StreamMetrics, StreamSource
from agrovision.domain.user import User
from agrovision.presentation.schemas import (
    BoundingBoxSchema,
    CountSampleSchema,
    DashboardSnapshot,
    DetectionSchema,
    ImagePredictionResponse,
    ModelInfoSchema,
    SessionRecordSchema,
    StreamMetricsSchema,
    StreamSchema,
    UserResponse,
    VideoPredictionResponse,
)


def detection_to_schema(detection: Detection, threshold: float) -> DetectionSchema:
    """Convert a domain detection to its API schema."""
    box = detection.box
    return DetectionSchema(
        label=detection.label,
        confidence=detection.confidence,
        confident=detection.is_confident(threshold),
        box=BoundingBoxSchema(x1=box.x1, y1=box.y1, x2=box.x2, y2=box.y2),
    )


def model_metadata_to_schema(metadata: ModelMetadata) -> ModelInfoSchema:
    """Convert model metadata to its API schema."""
    return ModelInfoSchema(
        name=metadata.name,
        version=metadata.version,
        weights_path=metadata.weights_path,
        weights_sha256=metadata.weights_sha256,
        device=metadata.device,
        image_size=metadata.image_size,
        confidence_threshold=metadata.confidence_threshold,
        classes=list(metadata.classes),
        limitations=list(metadata.limitations),
    )


def jpeg_to_data_url(jpeg: bytes) -> str:
    """Encode JPEG bytes as a base64 data URL."""
    encoded = base64.b64encode(jpeg).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def image_result_to_response(
    result: ImageDetectionResult, request_id: str, annotated_jpeg: bytes
) -> ImagePredictionResponse:
    """Build the image prediction response from the use-case result."""
    threshold = result.model.confidence_threshold
    return ImagePredictionResponse(
        request_id=request_id,
        model_version=result.model.version,
        confidence_threshold=threshold,
        width=result.frame.width,
        height=result.frame.height,
        count=result.count,
        uncertain_count=len(result.uncertain),
        mean_confidence=result.frame.mean_confidence,
        processing_ms=result.processing_ms,
        detections=[detection_to_schema(d, threshold) for d in result.frame.detections],
        annotated_image=jpeg_to_data_url(annotated_jpeg),
    )


def video_result_to_response(
    result: VideoDetectionResult, request_id: str, annotated_video_url: str
) -> VideoPredictionResponse:
    """Build the video prediction response from the use-case result."""
    summary = result.analysis.summary
    return VideoPredictionResponse(
        request_id=request_id,
        model_version=result.model.version,
        frames_processed=summary.frames_processed,
        max_count=summary.max_count,
        mean_count=summary.mean_count,
        peak_timestamp_s=summary.peak_timestamp_s,
        processing_ms=result.processing_ms,
        annotated_video_url=annotated_video_url,
        samples=[
            CountSampleSchema(
                timestamp_s=sample.timestamp_s,
                frame_index=sample.frame_index,
                count=sample.count,
            )
            for sample in summary.samples
        ],
        keyframes=[jpeg_to_data_url(jpeg) for jpeg in result.analysis.keyframes],
    )


def user_to_response(user: User) -> UserResponse:
    """Convert a domain user to its API schema."""
    return UserResponse(
        id=user.id, email=user.email, role=str(user.role), created_at=user.created_at
    )


def stream_to_schema(source: StreamSource) -> StreamSchema:
    """Convert a stream source to its API schema."""
    return StreamSchema(id=source.id, name=source.name, location=source.location, kind=source.kind)


def stream_metrics_to_schema(metrics: StreamMetrics) -> StreamMetricsSchema:
    """Convert stream metrics to their API schema."""
    return StreamMetricsSchema(
        stream_id=metrics.stream_id,
        status=str(metrics.status),
        sheep_count=metrics.sheep_count,
        mean_confidence=metrics.mean_confidence,
        latency_ms=metrics.latency_ms,
        frame_index=metrics.frame_index,
    )


def dashboard_to_snapshot(state: DashboardState) -> DashboardSnapshot:
    """Convert aggregate dashboard state to its API schema."""
    return DashboardSnapshot(
        total_sheep=state.total_sheep,
        active_streams=state.active_streams,
        streams=[stream_metrics_to_schema(metrics) for metrics in state.streams],
    )


def session_to_schema(record: SessionRecord) -> SessionRecordSchema:
    """Convert a session record to its API schema."""
    return SessionRecordSchema(
        id=record.id,
        kind=str(record.kind),
        source_name=record.source_name,
        sheep_count=record.sheep_count,
        mean_confidence=record.mean_confidence,
        model_version=record.model_version,
        created_at=record.created_at,
    )

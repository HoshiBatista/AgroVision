"""Image (and later video) inference endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from anyio import to_thread
from fastapi import APIRouter, Depends, File, Request, UploadFile

from agrovision.application.errors import UnsupportedMediaError, ValidationError
from agrovision.application.ports import DetectorPort
from agrovision.domain.report import NewSessionRecord, SessionKind
from agrovision.infrastructure.imaging import annotate, decode_image, encode_jpeg
from agrovision.presentation.presenters import (
    image_result_to_response,
    model_metadata_to_schema,
    video_result_to_response,
)
from agrovision.presentation.schemas import (
    ImagePredictionResponse,
    ModelInfoSchema,
    ModelThresholdRequest,
    VideoPredictionResponse,
)
from apps.api.dependencies import (
    CurrentUserDep,
    DetectImageDep,
    DetectVideoDep,
    OptionalUserIdDep,
    RequestIdDep,
    SettingsDep,
    StorageDep,
    get_detector,
)
from apps.api.journaling import record_session
from apps.api.uploads import ensure_image_type, ensure_video_type, read_limited

router = APIRouter(prefix="/v1", tags=["predictions"])


@router.get("/model-info", response_model=ModelInfoSchema)
async def model_info(detector: Annotated[DetectorPort, Depends(get_detector)]) -> ModelInfoSchema:
    """Return metadata for the loaded model."""
    return model_metadata_to_schema(detector.metadata)


@router.patch("/model-threshold", response_model=ModelInfoSchema)
async def update_model_threshold(
    payload: ModelThresholdRequest,
    _user: CurrentUserDep,
    detector: Annotated[DetectorPort, Depends(get_detector)],
) -> ModelInfoSchema:
    """Apply a runtime confidence threshold to every inference entry point."""
    setter = getattr(detector, "set_confidence_threshold", None)
    if not callable(setter):
        raise ValidationError("The active model does not support threshold changes")
    try:
        setter(payload.confidence_threshold)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    return model_metadata_to_schema(detector.metadata)


@router.post("/predictions", response_model=ImagePredictionResponse)
async def predict_image(
    request: Request,
    settings: SettingsDep,
    request_id: RequestIdDep,
    use_case: DetectImageDep,
    user_id: OptionalUserIdDep,
    file: Annotated[UploadFile, File(description="Image to analyse")],
) -> ImagePredictionResponse:
    """Detect and count sheep in a single uploaded image."""
    ensure_image_type(file.content_type)
    data = await read_limited(file, settings.max_upload_bytes)

    image = decode_image(data)
    if image is None:
        raise UnsupportedMediaError("Could not decode the uploaded image")

    height, width = image.shape[:2]
    if width * height > settings.max_image_pixels:
        raise ValidationError(f"Image resolution {width}x{height} exceeds the pixel limit")

    # Model work is synchronous and CPU/GPU-bound. Keep it outside the asyncio
    # event loop; the detector's bounded queue serializes access to the model.
    result = await to_thread.run_sync(use_case.execute, image)
    annotated = annotate(result.frame, image, result.model.confidence_threshold)
    annotated_jpeg = encode_jpeg(annotated, settings.stream_jpeg_quality)

    if user_id is not None:
        await record_session(
            request,
            NewSessionRecord(
                user_id=user_id,
                kind=SessionKind.IMAGE,
                source_name=file.filename or "image",
                sheep_count=result.count,
                mean_confidence=result.frame.mean_confidence,
                model_version=result.model.version,
                details={"processing_ms": round(result.processing_ms, 1)},
            ),
        )

    return image_result_to_response(result, request_id, annotated_jpeg)


@router.post("/predictions/video", response_model=VideoPredictionResponse)
async def predict_video(
    request: Request,
    settings: SettingsDep,
    request_id: RequestIdDep,
    storage: StorageDep,
    use_case: DetectVideoDep,
    user_id: OptionalUserIdDep,
    file: Annotated[UploadFile, File(description="Video to analyse")],
) -> VideoPredictionResponse:
    """Detect and count sheep across an uploaded video, frame by frame."""
    ensure_video_type(file.content_type)
    data = await read_limited(file, settings.max_upload_bytes)

    stem = Path(file.filename or "clip").stem or "clip"
    input_path = storage.write_bytes("videos/input", ".mp4", data, stem)
    output_path = storage.allocate("videos/annotated", ".mp4", stem)
    result = await to_thread.run_sync(use_case.execute, input_path, output_path)
    summary = result.analysis.summary

    if user_id is not None:
        await record_session(
            request,
            NewSessionRecord(
                user_id=user_id,
                kind=SessionKind.VIDEO,
                source_name=file.filename or "video",
                sheep_count=summary.max_count,
                mean_confidence=0.0,
                model_version=result.model.version,
                details={
                    "frames_processed": summary.frames_processed,
                    "peak_timestamp_s": round(summary.peak_timestamp_s, 2),
                },
            ),
        )

    return video_result_to_response(result, request_id, storage.media_url(result.output_path))

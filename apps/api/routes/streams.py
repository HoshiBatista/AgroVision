"""Drone stream listing and MJPEG video endpoints."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Response, status
from fastapi.responses import StreamingResponse

from agrovision.application.errors import ConflictError, NotFoundError
from agrovision.domain.stream import StreamSource
from agrovision.infrastructure.streaming.manager import StreamManager
from agrovision.presentation.presenters import stream_to_schema
from agrovision.presentation.schemas import ConnectRtspStreamRequest, StreamSchema
from apps.api.dependencies import CurrentUserDep, SettingsDep, StreamManagerDep

router = APIRouter(prefix="/v1/streams", tags=["streams"])

_BOUNDARY = "frame"
_PLACEHOLDER_INTERVAL = 0.5


@router.get("", response_model=list[StreamSchema])
async def list_streams(manager: StreamManagerDep) -> list[StreamSchema]:
    """List the configured drone streams."""
    return [stream_to_schema(source) for source in manager.sources()]


@router.post("", response_model=StreamSchema, status_code=status.HTTP_201_CREATED)
async def connect_rtsp_stream(
    payload: ConnectRtspStreamRequest,
    manager: StreamManagerDep,
    _user: CurrentUserDep,
) -> StreamSchema:
    """Attach an authenticated RTSP source to the running dashboard."""
    stream_id = payload.id or f"rtsp-{uuid.uuid4().hex[:8]}"
    source = StreamSource(
        id=stream_id,
        name=payload.name.strip(),
        location=payload.location.strip(),
        uri=payload.uri,
        kind="rtsp",
    )
    try:
        manager.add_source(source)
    except ValueError as exc:
        raise ConflictError("A stream with this id already exists") from exc
    return stream_to_schema(source)


@router.delete("/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_rtsp_stream(
    stream_id: str,
    manager: StreamManagerDep,
    _user: CurrentUserDep,
) -> Response:
    """Disconnect a runtime RTSP source; configured file streams stay protected."""
    if not manager.remove_source(stream_id):
        raise NotFoundError(f"Removable RTSP stream not found: {stream_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _mjpeg_frames(manager: StreamManager, stream_id: str, fps: int) -> AsyncIterator[bytes]:
    interval = 1.0 / fps
    header = f"--{_BOUNDARY}\r\nContent-Type: image/jpeg\r\n\r\n".encode()
    while True:
        jpeg = manager.latest_jpeg(stream_id)
        if jpeg is not None:
            yield header + jpeg + b"\r\n"
            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(_PLACEHOLDER_INTERVAL)


@router.get("/{stream_id}/mjpeg")
async def stream_mjpeg(
    stream_id: str, manager: StreamManagerDep, settings: SettingsDep
) -> StreamingResponse:
    """Return an MJPEG multipart stream of annotated frames for a drone feed."""
    if not manager.has_stream(stream_id):
        raise NotFoundError(f"Unknown stream: {stream_id}")
    return StreamingResponse(
        _mjpeg_frames(manager, stream_id, settings.stream_target_fps),
        media_type=f"multipart/x-mixed-replace; boundary={_BOUNDARY}",
    )

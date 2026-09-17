"""Safe upload reading and validation."""

from __future__ import annotations

from fastapi import UploadFile

from agrovision.application.errors import PayloadTooLargeError, UnsupportedMediaError

_IMAGE_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/webp"}
_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm", "video/avi"}
_CHUNK = 1024 * 1024


async def read_limited(file: UploadFile, max_bytes: int) -> bytes:
    """Read an upload fully while enforcing a maximum size."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(_CHUNK)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise PayloadTooLargeError(f"Upload exceeds the {max_bytes} byte limit")
        chunks.append(chunk)
    if total == 0:
        raise UnsupportedMediaError("Uploaded file is empty")
    return b"".join(chunks)


def ensure_image_type(content_type: str | None) -> None:
    """Reject uploads whose declared type is not a supported image."""
    if content_type is None or content_type.split(";")[0].strip() not in _IMAGE_TYPES:
        raise UnsupportedMediaError(f"Unsupported image type: {content_type!r}")


def ensure_video_type(content_type: str | None) -> None:
    """Reject uploads whose declared type is not a supported video."""
    if content_type is None or content_type.split(";")[0].strip() not in _VIDEO_TYPES:
        raise UnsupportedMediaError(f"Unsupported video type: {content_type!r}")

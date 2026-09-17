"""OpenCV/FFmpeg adapter for a live RTSP camera feed."""

from __future__ import annotations

from collections.abc import Iterator
from typing import cast

import cv2

from agrovision.application.ports import Image
from agrovision.domain.stream import StreamSource


class RtspStreamSource:
    """Yield frames from one RTSP connection until it closes or fails."""

    def __init__(self, source: StreamSource, open_timeout_ms: int, read_timeout_ms: int) -> None:
        self._source = source
        self._open_timeout_ms = open_timeout_ms
        self._read_timeout_ms = read_timeout_ms

    @property
    def source(self) -> StreamSource:
        """The safe source metadata; its URI is never returned by the API."""
        return self._source

    def frames(self) -> Iterator[Image]:
        """Open the camera and yield decoded BGR frames."""
        capture = cv2.VideoCapture()
        capture.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self._open_timeout_ms)
        capture.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, self._read_timeout_ms)
        opened = capture.open(self._source.uri, cv2.CAP_FFMPEG)
        if not opened:
            capture.release()
            raise ConnectionError("Could not connect to the RTSP source")
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                yield cast(Image, frame)
        finally:
            capture.release()

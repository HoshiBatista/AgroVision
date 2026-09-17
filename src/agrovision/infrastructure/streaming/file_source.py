"""File-backed stream source that loops a video file to simulate a live feed."""

from __future__ import annotations

from collections.abc import Iterator
from typing import cast

import cv2

from agrovision.application.ports import Image
from agrovision.domain.stream import StreamSource


class FileStreamSource:
    """Yields frames from a local video file, looping at end-of-file."""

    def __init__(self, source: StreamSource) -> None:
        self._source = source

    @property
    def source(self) -> StreamSource:
        """The stream configuration this source reads from."""
        return self._source

    def frames(self) -> Iterator[Image]:
        """Yield BGR frames indefinitely, restarting the file when it ends."""
        capture = cv2.VideoCapture(self._source.uri)
        if not capture.isOpened():
            raise FileNotFoundError(f"Cannot open stream source: {self._source.uri}")
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = capture.read()
                    if not ok:
                        break
                yield cast(Image, frame)
        finally:
            capture.release()

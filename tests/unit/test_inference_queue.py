"""Concurrency tests for the bounded single-worker detector queue."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import numpy as np
import pytest

from agrovision.application.errors import InferenceBusyError
from agrovision.application.ports import Image
from agrovision.domain.counting import FrameResult
from agrovision.domain.model import ModelMetadata
from agrovision.infrastructure.ml.inference_queue import QueuedDetector


class BlockingDetector:
    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()
        self._metadata = ModelMetadata(
            name="blocking",
            version="test",
            weights_path="memory://blocking",
            weights_sha256="0" * 64,
            device="cpu",
            image_size=32,
            confidence_threshold=0.4,
            classes=("sheep",),
        )

    @property
    def metadata(self) -> ModelMetadata:
        return self._metadata

    def detect(self, image: Image) -> FrameResult:
        self.started.set()
        self.release.wait(timeout=2)
        height, width = image.shape[:2]
        return FrameResult((), int(width), int(height))


def test_queue_rejects_work_over_capacity() -> None:
    inner = BlockingDetector()
    detector = QueuedDetector(
        inner,
        capacity=1,
        queue_wait_seconds=0.01,
        inference_timeout_seconds=2,
    )
    image = np.zeros((32, 32, 3), dtype=np.uint8)

    with ThreadPoolExecutor(max_workers=1) as callers:
        first = callers.submit(detector.detect, image)
        assert inner.started.wait(timeout=1)
        with pytest.raises(InferenceBusyError):
            detector.detect(image)
        inner.release.set()
        assert first.result(timeout=1).width == 32

    detector.close()

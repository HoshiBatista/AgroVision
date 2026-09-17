"""Unit tests for the image detection use case and imaging helpers."""

from __future__ import annotations

import numpy as np

from agrovision.application.use_cases.detect_image import DetectImageUseCase
from agrovision.infrastructure.imaging import annotate, decode_image, encode_jpeg
from tests.fakes import FakeDetector


def _synthetic_jpeg() -> bytes:
    image = np.full((120, 160, 3), 127, dtype=np.uint8)
    return encode_jpeg(image, quality=90)


def test_detect_image_use_case_wraps_metadata() -> None:
    use_case = DetectImageUseCase(FakeDetector())
    image = np.zeros((100, 100, 3), dtype=np.uint8)

    result = use_case.execute(image)

    assert result.count == 1
    assert result.processing_ms >= 0.0
    assert result.model.classes == ("sheep",)
    assert len(result.uncertain) == 1  # the 0.2-confidence detection


def test_decode_annotate_encode_roundtrip() -> None:
    image = decode_image(_synthetic_jpeg())
    assert image is not None
    assert image.shape == (120, 160, 3)

    use_case = DetectImageUseCase(FakeDetector())
    result = use_case.execute(image)
    annotated = annotate(result.frame, image, result.model.confidence_threshold)

    assert annotated.shape == image.shape
    assert encode_jpeg(annotated)  # non-empty bytes


def test_decode_image_rejects_garbage() -> None:
    assert decode_image(b"not an image") is None

"""Image decoding, annotation, and encoding helpers (OpenCV boundary)."""

from __future__ import annotations

import cv2
import numpy as np
from numpy.typing import NDArray

from agrovision.domain.counting import FrameResult
from agrovision.domain.detection import Detection

Image = NDArray[np.uint8]

_CONFIDENT_COLOR = (46, 204, 113)  # green (BGR)
_UNCERTAIN_COLOR = (39, 174, 239)  # amber (BGR)


def decode_image(data: bytes) -> Image | None:
    """Decode raw image bytes into a BGR array, or None if unreadable."""
    buffer = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        return None
    return image.astype(np.uint8)


def annotate(frame: FrameResult, image: Image, confidence_threshold: float) -> Image:
    """Draw bounding boxes and a count badge onto a copy of the image."""
    canvas = image.copy()
    for detection in frame.detections:
        _draw_detection(canvas, detection, confidence_threshold)
    _draw_count_badge(canvas, frame.count_above(confidence_threshold))
    return canvas


def _draw_detection(canvas: Image, detection: Detection, confidence_threshold: float) -> None:
    color = _CONFIDENT_COLOR if detection.is_confident(confidence_threshold) else _UNCERTAIN_COLOR
    box = detection.box
    p1 = (int(box.x1), int(box.y1))
    p2 = (int(box.x2), int(box.y2))
    cv2.rectangle(canvas, p1, p2, color, 2)
    label = f"{detection.label} {detection.confidence:.2f}"
    origin = (p1[0], max(0, p1[1] - 6))
    cv2.putText(canvas, label, origin, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)


def _draw_count_badge(canvas: Image, count: int) -> None:
    text = str(count)
    cv2.rectangle(canvas, (8, 8), (8 + 12 * len(text), 40), (33, 37, 41), -1)
    cv2.putText(
        canvas, text, (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA
    )


def encode_jpeg(image: Image, quality: int = 85) -> bytes:
    """Encode a BGR image array as JPEG bytes."""
    success, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not success:
        raise RuntimeError("Failed to encode image as JPEG")
    return buffer.tobytes()

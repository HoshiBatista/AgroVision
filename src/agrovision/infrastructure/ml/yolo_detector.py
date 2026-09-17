"""YOLO-based implementation of the DetectorPort."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import torch
from ultralytics import YOLO

from agrovision.application.ports import Image
from agrovision.config import Settings
from agrovision.domain.counting import FrameResult
from agrovision.domain.detection import BoundingBox, Detection
from agrovision.domain.model import ModelMetadata
from agrovision.infrastructure.ml.inference_queue import QueuedDetector

_LEAKAGE_LIMITATION = (
    "В исходном разбиении есть соседние кадры DJI-видео в обучающей и тестовой "
    "выборках; метрики могут быть завышены до пересборки разбиения."
)
_ESTIMATE_LIMITATION = (
    "Подсчёт является визуальной оценкой: перекрытия, плотность стада и высота "
    "полёта могут приводить к пропускам или повторным детекциям."
)


def resolve_device(requested: str) -> str:
    """Resolve 'auto' to CUDA, Apple MPS, or CPU."""
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _sha256(path: Path) -> str:
    """Return the SHA-256 digest of a model artifact without loading it."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_weights(settings: Settings) -> tuple[Path, str, str]:
    """Return the weights path and a human-readable model version string."""
    trained = settings.detector_model_path
    if trained.exists():
        actual_hash = _sha256(trained)
        expected_hash = settings.detector_model_sha256.lower()
        if expected_hash and actual_hash != expected_hash:
            raise RuntimeError(
                f"Model checksum mismatch for {trained}: expected {expected_hash}, "
                f"got {actual_hash}"
            )
        return trained, settings.detector_model_version, actual_hash
    if settings.detector_allow_fallback:
        fallback = Path(settings.detector_fallback_checkpoint)
        return fallback, "pretrained-yolo26n-fallback", "unverified"
    raise FileNotFoundError(
        f"Selected model is missing: {trained}. Restore the versioned best.pt artifact "
        "or explicitly set DETECTOR_ALLOW_FALLBACK=true for development."
    )


class YoloDetector:
    """Loads a YOLO model once and runs single-image detection."""

    def __init__(self, settings: Settings) -> None:
        weights, version, weights_sha256 = _resolve_weights(settings)
        self._device = resolve_device(settings.model_device)
        self._image_size = settings.detector_image_size
        self._inference_floor = settings.detector_inference_floor
        self._confidence = settings.detector_confidence_threshold
        self._model = YOLO(str(weights))
        self._names: dict[int, str] = dict(self._model.names)
        self._class_ids = [
            class_id
            for class_id, label in self._names.items()
            if label == settings.detector_target_class
        ]
        if not self._class_ids:
            raise RuntimeError(
                f"Target class {settings.detector_target_class!r} is absent from {weights}"
            )
        limitations = [_ESTIMATE_LIMITATION, _LEAKAGE_LIMITATION]
        if version.endswith("-fallback"):
            limitations.insert(
                0,
                "Используется резервная модель COCO; точность на аэросъёмке не проверена.",
            )
        self._metadata = ModelMetadata(
            name="YOLO26n · детектор овец с дрона",
            version=version,
            weights_path=str(weights),
            weights_sha256=weights_sha256,
            device=self._device,
            image_size=self._image_size,
            confidence_threshold=self._confidence,
            classes=(settings.detector_target_class,),
            limitations=tuple(limitations),
        )

    @property
    def metadata(self) -> ModelMetadata:
        """Descriptive metadata about the loaded model."""
        return self._metadata

    def detect(self, image: Image) -> FrameResult:
        """Run detection on a single BGR image array."""
        results = cast(
            list[Any],
            self._model.predict(
                image,
                imgsz=self._image_size,
                conf=self._inference_floor,
                classes=self._class_ids,
                device=self._device,
                verbose=False,
            ),
        )
        result = results[0]
        detections: list[Detection] = []
        boxes = result.boxes
        if boxes is not None:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            classes = boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), conf, cls in zip(xyxy, confs, classes, strict=True):
                detections.append(
                    Detection(
                        label=self._names.get(int(cls), str(cls)),
                        confidence=float(conf),
                        box=BoundingBox(float(x1), float(y1), float(x2), float(y2)),
                    )
                )
        height, width = image.shape[:2]
        return FrameResult(
            detections=tuple(detections),
            width=int(width),
            height=int(height),
        )

    def set_confidence_threshold(self, threshold: float) -> None:
        """Update the operational counting threshold for future results."""
        if not self._inference_floor <= threshold <= 0.95:
            raise ValueError(
                f"Confidence threshold must be between {self._inference_floor:.2f} and 0.95"
            )
        self._confidence = threshold
        self._metadata = replace(self._metadata, confidence_threshold=threshold)


def build_detector(settings: Settings) -> QueuedDetector:
    """Load the selected model once and wrap it in the shared bounded queue."""
    return QueuedDetector(
        YoloDetector(settings),
        capacity=settings.detector_queue_capacity,
        queue_wait_seconds=settings.detector_queue_wait_seconds,
        inference_timeout_seconds=settings.detector_inference_timeout_seconds,
    )

"""Model metadata value object surfaced through the API."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    """Descriptive metadata about the loaded detection model."""

    name: str
    version: str
    weights_path: str
    weights_sha256: str
    device: str
    image_size: int
    confidence_threshold: float
    classes: tuple[str, ...]
    limitations: tuple[str, ...] = field(default_factory=tuple)

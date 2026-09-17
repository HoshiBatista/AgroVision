"""Detection value objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned bounding box in absolute pixel coordinates."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        if self.x2 < self.x1 or self.y2 < self.y1:
            raise ValueError("BoundingBox requires x2 >= x1 and y2 >= y1")

    @property
    def width(self) -> float:
        """Box width in pixels."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Box height in pixels."""
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        """Box area in square pixels."""
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        """Box center as (x, y)."""
        return (self.x1 + self.width / 2, self.y1 + self.height / 2)


@dataclass(frozen=True, slots=True)
class Detection:
    """A single detected object with its class label and confidence."""

    label: str
    confidence: float
    box: BoundingBox

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")

    def is_confident(self, threshold: float) -> bool:
        """Return whether the detection meets the given confidence threshold."""
        return self.confidence >= threshold

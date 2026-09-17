"""Frame-level and aggregate counting value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import fmean

from agrovision.domain.detection import Detection


@dataclass(frozen=True, slots=True)
class FrameResult:
    """Detections and dimensions for a single analysed frame or image."""

    detections: tuple[Detection, ...]
    width: int
    height: int
    frame_index: int = 0
    timestamp_s: float = 0.0

    @property
    def count(self) -> int:
        """Number of detected objects."""
        return len(self.detections)

    @property
    def mean_confidence(self) -> float:
        """Mean confidence across detections, or 0.0 when empty."""
        if not self.detections:
            return 0.0
        return fmean(detection.confidence for detection in self.detections)

    def uncertain(self, threshold: float) -> tuple[Detection, ...]:
        """Return detections below the confidence threshold."""
        return tuple(d for d in self.detections if not d.is_confident(threshold))

    def confident(self, threshold: float) -> tuple[Detection, ...]:
        """Return detections included in the operational count."""
        return tuple(d for d in self.detections if d.is_confident(threshold))

    def count_above(self, threshold: float) -> int:
        """Count detections at or above the operational threshold."""
        return len(self.confident(threshold))


@dataclass(frozen=True, slots=True)
class CountSample:
    """A single point in a count-over-time series."""

    timestamp_s: float
    frame_index: int
    count: int


@dataclass(frozen=True, slots=True)
class VideoCountSummary:
    """Aggregate statistics for a processed video."""

    frames_processed: int
    max_count: int
    mean_count: float
    peak_timestamp_s: float
    samples: tuple[CountSample, ...] = field(default_factory=tuple)

    @classmethod
    def from_samples(cls, samples: list[CountSample]) -> VideoCountSummary:
        """Build a summary from an ordered list of count samples."""
        if not samples:
            return cls(0, 0, 0.0, 0.0, ())
        peak = max(samples, key=lambda sample: sample.count)
        return cls(
            frames_processed=len(samples),
            max_count=peak.count,
            mean_count=fmean(sample.count for sample in samples),
            peak_timestamp_s=peak.timestamp_s,
            samples=tuple(samples),
        )

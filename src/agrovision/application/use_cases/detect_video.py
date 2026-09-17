"""Use case: detect and count sheep across an uploaded video."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from agrovision.application.dto import VideoAnalysis
from agrovision.application.ports import VideoAnalyzerPort
from agrovision.domain.model import ModelMetadata


@dataclass(frozen=True, slots=True)
class VideoDetectionResult:
    """The result of analysing a video, with timing and model metadata."""

    analysis: VideoAnalysis
    processing_ms: float
    model: ModelMetadata
    output_path: Path


class DetectVideoUseCase:
    """Runs the video analyzer and wraps the result with metadata."""

    def __init__(self, analyzer: VideoAnalyzerPort) -> None:
        self._analyzer = analyzer

    def execute(self, input_path: Path, output_path: Path) -> VideoDetectionResult:
        """Analyse a video file and write an annotated output video."""
        started = time.perf_counter()
        analysis = self._analyzer.analyze(input_path, output_path)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return VideoDetectionResult(
            analysis=analysis,
            processing_ms=elapsed_ms,
            model=self._analyzer.metadata,
            output_path=output_path,
        )

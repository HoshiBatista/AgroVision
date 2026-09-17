"""OpenCV-based video analyzer implementing the VideoAnalyzerPort."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import cv2

from agrovision.application.dto import VideoAnalysis
from agrovision.application.errors import UnsupportedMediaError
from agrovision.application.ports import DetectorPort, Image
from agrovision.config import Settings
from agrovision.domain.counting import CountSample, VideoCountSummary
from agrovision.domain.model import ModelMetadata
from agrovision.infrastructure.imaging import annotate, encode_jpeg

_DEFAULT_FPS = 25.0


class VideoAnalyzer:
    """Reads a video, runs detection on sampled frames, and writes annotations."""

    def __init__(self, detector: DetectorPort, settings: Settings) -> None:
        self._detector = detector
        self._stride = max(1, settings.stream_frame_stride)
        self._quality = settings.stream_jpeg_quality
        self._max_frames = settings.video_max_processed_frames
        self._keyframe_target = settings.video_keyframes

    @property
    def metadata(self) -> ModelMetadata:
        """Descriptive metadata about the underlying model."""
        return self._detector.metadata

    def analyze(self, input_path: Path, output_path: Path) -> VideoAnalysis:
        """Analyse a video file and write an annotated output video."""
        capture = cv2.VideoCapture(str(input_path))
        if not capture.isOpened():
            raise UnsupportedMediaError("Could not open the uploaded video")
        try:
            return self._run(capture, output_path)
        finally:
            capture.release()

    def _run(self, capture: cv2.VideoCapture, output_path: Path) -> VideoAnalysis:
        fps = capture.get(cv2.CAP_PROP_FPS) or _DEFAULT_FPS
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        threshold = self._detector.metadata.confidence_threshold

        writer = self._open_writer(output_path, max(1.0, fps / self._stride), width, height)
        estimated = min(self._max_frames, max(1, total_frames // self._stride))
        keyframe_every = max(1, estimated // self._keyframe_target)

        samples: list[CountSample] = []
        keyframes: list[bytes] = []
        index = 0
        try:
            while len(samples) < self._max_frames:
                ok, frame = capture.read()
                if not ok:
                    break
                if index % self._stride == 0:
                    bgr = cast(Image, frame)
                    result = self._detector.detect(bgr)
                    annotated = annotate(result, bgr, threshold)
                    writer.write(annotated)
                    samples.append(
                        CountSample(
                            timestamp_s=index / fps,
                            frame_index=index,
                            count=result.count_above(threshold),
                        )
                    )
                    if (
                        len(keyframes) < self._keyframe_target
                        and (len(samples) - 1) % keyframe_every == 0
                    ):
                        keyframes.append(encode_jpeg(annotated, self._quality))
                index += 1
        finally:
            writer.release()

        return VideoAnalysis(
            summary=VideoCountSummary.from_samples(samples),
            keyframes=tuple(keyframes),
        )

    @staticmethod
    def _open_writer(path: Path, fps: float, width: int, height: int) -> cv2.VideoWriter:
        for codec in ("avc1", "mp4v"):
            fourcc = cv2.VideoWriter.fourcc(*codec)
            writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
            if writer.isOpened():
                return writer
        raise UnsupportedMediaError("No available codec to write the annotated video")

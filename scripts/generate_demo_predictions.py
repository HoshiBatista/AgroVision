"""Generate an offline gallery by running the selected model on local demo media."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import cv2

from agrovision.application.ports import Image
from agrovision.config import Settings
from agrovision.infrastructure.imaging import annotate
from agrovision.infrastructure.ml.yolo_detector import YoloDetector
from agrovision.infrastructure.video import VideoAnalyzer

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, default=Path("data/raw/aerial-sheep-1/test/images"))
    parser.add_argument("--labels", type=Path, default=Path("data/raw/aerial-sheep-1/test/labels"))
    parser.add_argument(
        "--videos",
        type=Path,
        nargs="+",
        default=[Path("data/demo"), Path(".")],
        help="Directories with MP4 files (default: data/demo and repository root)",
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/demo_predictions"))
    parser.add_argument("--image-count", type=int, default=6)
    return parser.parse_args()


def _label_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text().splitlines() if line.strip())


def _representative_images(
    images_dir: Path, labels_dir: Path, count: int
) -> list[tuple[Path, int]]:
    ranked = sorted(
        (
            (path, _label_count(labels_dir / f"{path.stem}.txt"))
            for path in images_dir.iterdir()
            if path.suffix.lower() in IMAGE_SUFFIXES
        ),
        key=lambda item: (item[1], item[0].name),
    )
    ranked = [item for item in ranked if item[1] > 0]
    if not ranked:
        raise SystemExit(f"No test images found in {images_dir}")
    target = max(1, min(count, len(ranked)))
    indexes = [round(index * (len(ranked) - 1) / max(1, target - 1)) for index in range(target)]
    return [ranked[index] for index in dict.fromkeys(indexes)]


def _transcode_for_browser(raw_path: Path, final_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raw_path.replace(final_path)
        return
    completed = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(raw_path),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(final_path),
        ],
        check=False,
    )
    if completed.returncode == 0:
        raw_path.unlink(missing_ok=True)
    else:
        raw_path.replace(final_path)


def _generate_images(
    detector: YoloDetector,
    selected: list[tuple[Path, int]],
    output_root: Path,
) -> list[dict[str, Any]]:
    output_dir = output_root / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    threshold = detector.metadata.confidence_threshold
    for index, (source, expected_count) in enumerate(selected, start=1):
        decoded = cv2.imread(str(source))
        if decoded is None:
            continue
        image = cast(Image, decoded)
        started = time.perf_counter()
        result = detector.detect(image)
        elapsed_ms = (time.perf_counter() - started) * 1000
        output_name = f"example-{index:02d}.jpg"
        output_path = output_dir / output_name
        cv2.imwrite(str(output_path), annotate(result, image, threshold))
        confidences = [d.confidence for d in result.detections]
        records.append(
            {
                "name": source.name,
                "url": f"/demo-media/images/{output_name}",
                "ground_truth_count": expected_count,
                "count": result.count_above(threshold),
                "uncertain_count": len(result.uncertain(threshold)),
                "mean_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                "processing_ms": elapsed_ms,
            }
        )
        count = result.count_above(threshold)
        print(f"image {index}/{len(selected)}: {source.name} -> {count} sheep")
    return records


def _generate_videos(
    detector: YoloDetector,
    video_dirs: list[Path],
    output_root: Path,
    settings: Settings,
) -> list[dict[str, Any]]:
    output_dir = output_root / "videos"
    poster_dir = output_root / "posters"
    output_dir.mkdir(parents=True, exist_ok=True)
    poster_dir.mkdir(parents=True, exist_ok=True)
    analyzer = VideoAnalyzer(detector, settings)
    records: list[dict[str, Any]] = []
    sources = sorted(
        {path.resolve() for directory in video_dirs for path in directory.glob("*.mp4")}
    )
    for index, source in enumerate(sources, start=1):
        print(f"video {index}/{len(sources)}: processing {source.name} ...", flush=True)
        raw_path = output_dir / f"{source.stem}.raw.mp4"
        final_path = output_dir / source.name
        started = time.perf_counter()
        analysis = analyzer.analyze(source, raw_path)
        processing_ms = (time.perf_counter() - started) * 1000
        _transcode_for_browser(raw_path, final_path)
        poster_url: str | None = None
        if analysis.keyframes:
            poster_name = f"{source.stem}.jpg"
            (poster_dir / poster_name).write_bytes(analysis.keyframes[0])
            poster_url = f"/demo-media/posters/{poster_name}"
        summary = analysis.summary
        records.append(
            {
                "name": source.name,
                "url": f"/demo-media/videos/{source.name}",
                "poster_url": poster_url,
                "frames_processed": len(summary.samples),
                "max_count": summary.max_count,
                "mean_count": summary.mean_count,
                "peak_timestamp_s": summary.peak_timestamp_s,
                "processing_ms": processing_ms,
            }
        )
        print(f"video {index}/{len(sources)}: done, peak {summary.max_count} sheep")
    return records


def main() -> None:
    args = parse_args()
    settings = Settings()
    output_root: Path = args.output
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    detector = YoloDetector(settings)
    selected = _representative_images(args.images, args.labels, args.image_count)
    warmup_decoded = cv2.imread(str(selected[0][0]))
    if warmup_decoded is not None:
        detector.detect(cast(Image, warmup_decoded))
    images = _generate_images(detector, selected, output_root)
    videos = _generate_videos(detector, args.videos, output_root, settings)
    metadata = detector.metadata
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "model": {
            "name": metadata.name,
            "version": metadata.version,
            "device": metadata.device,
            "weights_sha256": metadata.weights_sha256,
        },
        "images": images,
        "videos": videos,
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"generated {len(images)} images and {len(videos)} videos -> {output_root}")


if __name__ == "__main__":
    main()

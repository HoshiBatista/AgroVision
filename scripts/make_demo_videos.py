"""Generate simulated drone-stream videos from aerial-sheep dataset frames.

Each configured stream in ``configs/app.toml`` gets a short looping MP4 stitched
from a disjoint slice of dataset images. This keeps the live-stream demo fully
offline and reproducible without real drone hardware.

Usage:
    uv run python -m scripts.make_demo_videos
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

import cv2

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_FRAME_SIZE = (1280, 720)
_FPS = 8.0
_FRAMES_PER_STREAM = 60


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, default=Path("data/raw/aerial-sheep-1/test/images"))
    parser.add_argument("--config", type=Path, default=Path("configs/app.toml"))
    parser.add_argument("--output", type=Path, default=Path("data/demo"))
    return parser.parse_args()


def _stream_ids(config_path: Path) -> list[str]:
    data = tomllib.loads(config_path.read_text())
    return [str(entry["id"]) for entry in data.get("streams", [])]


def _list_images(images_dir: Path) -> list[Path]:
    if not images_dir.exists():
        raise SystemExit(f"Dataset images not found: {images_dir}. Run `make prepare` first.")
    images = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in _IMAGE_SUFFIXES)
    if not images:
        raise SystemExit(f"No images found in {images_dir}")
    return images


def _write_video(frames: list[Path], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter.fourcc(*"mp4v"), _FPS, _FRAME_SIZE)
    written = 0
    for image_path in frames:
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        writer.write(cv2.resize(image, _FRAME_SIZE))
        written += 1
    writer.release()
    return written


def main() -> None:
    """Generate one looping demo video per configured stream."""
    args = parse_args()
    stream_ids = _stream_ids(args.config)
    images = _list_images(args.images)

    per_stream = max(1, min(_FRAMES_PER_STREAM, len(images) // max(1, len(stream_ids))))
    for index, stream_id in enumerate(stream_ids):
        start = index * per_stream
        slice_ = images[start : start + per_stream] or images[:per_stream]
        output_path = args.output / f"{stream_id}.mp4"
        written = _write_video(slice_, output_path)
        print(f"{stream_id}: wrote {written} frames -> {output_path}")


if __name__ == "__main__":
    main()

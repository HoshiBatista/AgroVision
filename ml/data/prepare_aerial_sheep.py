"""Prepare a clean YOLO view of the immutable Aerial Sheep v1 export."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import yaml

SPLITS = ("train", "valid", "test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("data/raw/aerial-sheep-1"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/aerial-sheep-1-yolo"))
    return parser.parse_args()


def valid_yolo_row(row: str) -> bool:
    """Return whether a row is a valid one-class normalized detection label."""
    fields = row.split()
    if len(fields) != 5:
        return False
    try:
        class_id = int(fields[0])
        x, y, width, height = (float(value) for value in fields[1:])
    except ValueError:
        return False
    return (
        class_id == 0
        and 0.0 <= x <= 1.0
        and 0.0 <= y <= 1.0
        and 0.0 < width <= 1.0
        and 0.0 < height <= 1.0
        and x - width / 2 >= -1e-6
        and y - height / 2 >= -1e-6
        and x + width / 2 <= 1.0 + 1e-6
        and y + height / 2 <= 1.0 + 1e-6
    )


def relative_symlink(source: Path, destination: Path) -> None:
    """Create a relative symlink."""
    destination.symlink_to(os.path.relpath(source.resolve(), destination.parent.resolve()))


def prepare(raw_root: Path, output_root: Path) -> dict[str, object]:
    """Link images, clean labels, and return preparation statistics."""
    raw_root = raw_root.resolve()
    if not (raw_root / "data.yaml").exists():
        raise FileNotFoundError(f"Dataset is missing: {raw_root / 'data.yaml'}")

    output_root = output_root.resolve()
    expected_parent = Path.cwd().resolve() / "data" / "processed"
    if expected_parent not in output_root.parents:
        raise ValueError(f"Refusing to replace a path outside data/processed: {output_root}")
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    report: dict[str, object] = {"removed_invalid_boxes": 0, "splits": {}}
    split_report: dict[str, dict[str, int]] = {}
    removed_total = 0
    for split in SPLITS:
        source_images = raw_root / split / "images"
        source_labels = raw_root / split / "labels"
        target_split = output_root / split
        target_split.mkdir()
        target_images = target_split / "images"
        target_images.mkdir()
        target_labels = target_split / "labels"
        target_labels.mkdir()

        images = [path for path in source_images.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES]
        objects = 0
        removed = 0
        for image in images:
            relative_symlink(image, target_images / image.name)
            source_label = source_labels / f"{image.stem}.txt"
            rows = source_label.read_text().splitlines() if source_label.exists() else []
            clean_rows = [row.strip() for row in rows if row.strip() and valid_yolo_row(row)]
            removed += sum(bool(row.strip()) for row in rows) - len(clean_rows)
            objects += len(clean_rows)
            (target_labels / f"{image.stem}.txt").write_text(
                "\n".join(clean_rows) + ("\n" if clean_rows else "")
            )
        split_report[split] = {"images": len(images), "objects": objects, "removed": removed}
        removed_total += removed

    report["removed_invalid_boxes"] = removed_total
    report["splits"] = split_report
    data_config = {
        "path": str(output_root),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": {0: "sheep"},
    }
    (output_root / "data.yaml").write_text(yaml.safe_dump(data_config, sort_keys=False))
    (output_root / "preparation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    return report


def main() -> None:
    """Prepare the configured dataset view."""
    args = parse_args()
    report = prepare(args.raw, args.output)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

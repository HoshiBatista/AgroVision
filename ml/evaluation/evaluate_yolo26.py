"""Evaluate the trained YOLO26 sheep detector on the held-out test split.

Reports detection metrics (mAP50-95, mAP50, precision, recall), counting error
(MAE/RMSE of predicted vs. ground-truth counts), and inference latency (p50/p95).
The known split-leakage limitation from ADR 0001 is recorded alongside the metrics
so the numbers are never presented without that caveat.

Usage:
    uv run python -m ml.evaluation.evaluate_yolo26
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tomllib
from pathlib import Path
from typing import Any, cast

from ultralytics import YOLO

from ml.training.train_yolo26 import resolve_device

_LEAKAGE_NOTE = (
    "The downloaded split contains adjacent DJI video frames across train/val/test "
    "(ADR 0001). Random-split test metrics are optimistic until the split is rebuilt "
    "by source video/flight."
)
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/train_yolo26n_aerial_sheep.toml")
    )
    parser.add_argument("--weights", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation"))
    return parser.parse_args()


def _resolve_weights(config: dict[str, Any], override: Path | None) -> Path:
    if override is not None:
        return override
    training = config["training"]
    run_dir = Path(training["output_root"]) / str(training["run_name"])
    best = run_dir / "weights" / "best.pt"
    if best.exists():
        return best
    return Path(config["model"]["checkpoint"])


def _count_ground_truth(label_path: Path) -> int:
    if not label_path.exists():
        return 0
    return sum(1 for line in label_path.read_text().splitlines() if line.strip())


def _counting_and_latency(
    model: YOLO, images_dir: Path, labels_dir: Path, imgsz: int, conf: float, device: str
) -> dict[str, float]:
    images = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in _IMAGE_SUFFIXES)
    abs_errors: list[float] = []
    sq_errors: list[float] = []
    latencies_ms: list[float] = []
    for image in images:
        started = time.perf_counter()
        results = cast(
            list[Any],
            model.predict(str(image), imgsz=imgsz, conf=conf, device=device, verbose=False),
        )
        latencies_ms.append((time.perf_counter() - started) * 1000.0)
        predicted = len(results[0].boxes) if results[0].boxes is not None else 0
        truth = _count_ground_truth(labels_dir / f"{image.stem}.txt")
        error = predicted - truth
        abs_errors.append(abs(error))
        sq_errors.append(float(error * error))

    if not images:
        return {"count_mae": 0.0, "count_rmse": 0.0, "latency_p50_ms": 0.0, "latency_p95_ms": 0.0}
    ordered = sorted(latencies_ms)
    p95_index = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
    return {
        "images": float(len(images)),
        "count_mae": statistics.fmean(abs_errors),
        "count_rmse": (statistics.fmean(sq_errors)) ** 0.5,
        "latency_p50_ms": statistics.median(ordered),
        "latency_p95_ms": ordered[p95_index],
    }


def main() -> None:
    """Run the full evaluation and write a JSON + Markdown report."""
    args = parse_args()
    config = tomllib.loads(args.config.read_text())
    dataset_root = Path(config["dataset"]["root"])
    dataset_yaml = dataset_root / "data.yaml"
    if not dataset_yaml.exists():
        raise SystemExit(f"Prepared dataset is missing: {dataset_yaml}. Run `make prepare`.")

    weights = _resolve_weights(config, args.weights)
    imgsz = int(config["model"]["image_size"])
    device = resolve_device(str(config["training"]["device"]))
    conf = 0.25

    model = YOLO(str(weights))
    validation = model.val(data=str(dataset_yaml), split="test", imgsz=imgsz, device=device)
    box = validation.box

    counting = _counting_and_latency(
        model,
        dataset_root / "test" / "images",
        dataset_root / "test" / "labels",
        imgsz,
        conf,
        device,
    )

    report = {
        "weights": str(weights),
        "dataset": str(dataset_yaml),
        "device": device,
        "detection": {
            "map50_95": float(box.map),
            "map50": float(box.map50),
            "precision": float(box.mp),
            "recall": float(box.mr),
        },
        "counting": counting,
        "limitation": _LEAKAGE_NOTE,
    }

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "report.md").write_text(_render_markdown(report))
    print(json.dumps(report, indent=2))


def _render_markdown(report: dict[str, Any]) -> str:
    detection = report["detection"]
    counting = report["counting"]
    return (
        "# AgroVision evaluation report\n\n"
        f"- Weights: `{report['weights']}`\n"
        f"- Device: {report['device']}\n\n"
        "## Detection (test split)\n\n"
        f"- mAP50-95: {detection['map50_95']:.4f}\n"
        f"- mAP50: {detection['map50']:.4f}\n"
        f"- Precision: {detection['precision']:.4f}\n"
        f"- Recall: {detection['recall']:.4f}\n\n"
        "## Counting and latency\n\n"
        f"- Count MAE: {counting['count_mae']:.3f}\n"
        f"- Count RMSE: {counting['count_rmse']:.3f}\n"
        f"- Latency p50: {counting['latency_p50_ms']:.1f} ms\n"
        f"- Latency p95: {counting['latency_p95_ms']:.1f} ms\n\n"
        "## Limitation\n\n"
        f"{report['limitation']}\n"
    )


if __name__ == "__main__":
    main()

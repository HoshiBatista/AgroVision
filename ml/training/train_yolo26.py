"""Fine-tune YOLO26 Nano on the prepared Aerial Sheep dataset."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

import torch
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/train_yolo26n_aerial_sheep.toml")
    )
    return parser.parse_args()


def resolve_device(requested: str) -> str:
    """Resolve auto to CUDA, Apple MPS, or CPU."""
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> None:
    """Run the configured fine-tuning job."""
    args = parse_args()
    config = tomllib.loads(args.config.read_text())
    dataset_yaml = Path(config["dataset"]["root"]) / "data.yaml"
    if not dataset_yaml.exists():
        raise SystemExit(f"Prepared dataset is missing: {dataset_yaml}. Run `make prepare`.")

    training = config["training"]
    device = resolve_device(str(training["device"]))
    output_root = Path(training["output_root"]).resolve()
    run_dir = output_root / str(training["run_name"])
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "config": str(args.config),
        "dataset": str(dataset_yaml),
        "checkpoint": config["model"]["checkpoint"],
        "device": device,
        "epochs": training["epochs"],
        "batch_size": training["batch_size"],
        "seed": training["seed"],
        "known_limitation": "Roboflow split contains adjacent DJI video frames across splits.",
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )

    model = YOLO(str(config["model"]["checkpoint"]))
    model.train(
        data=str(dataset_yaml),
        epochs=int(training["epochs"]),
        imgsz=int(config["model"]["image_size"]),
        batch=int(training["batch_size"]),
        workers=int(training["workers"]),
        device=device,
        seed=int(training["seed"]),
        deterministic=True,
        patience=int(training["patience"]),
        cache=False,
        project=str(output_root),
        name=str(training["run_name"]),
        exist_ok=True,
        plots=True,
    )


if __name__ == "__main__":
    main()

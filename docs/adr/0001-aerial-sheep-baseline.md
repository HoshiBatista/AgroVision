# ADR 0001: Aerial sheep detection baseline

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-09-12 |
| Owners | AgroVision team |
| Decision area | Dataset, training, and evaluation |

## Context

The product needs a compact detector that can count sheep in aerial imagery on
developer hardware and remain practical for an interactive demo. The selected
public dataset is Roboflow `riis/aerial-sheep`, version 1.

The published split is convenient for a baseline but is not independent at the
flight level: adjacent frames from the same DJI videos appear across train,
validation, and test.

## Decision

Fine-tune `yolo26n.pt` at 640 px for one detection class, `sheep`. Use the
Roboflow version 1 export as immutable raw input and generate a separate cleaned
YOLO view for training.

The reproducible training configuration is
[`configs/train_yolo26n_aerial_sheep.toml`](../../configs/train_yolo26n_aerial_sheep.toml):

- maximum 50 epochs with early stopping;
- batch size 16;
- fixed seed 42;
- automatic CUDA, Apple MPS, or CPU device selection;
- no hidden dataset cache or hosted inference dependency.

## Dataset snapshot

| Property | Value |
|---|---:|
| Task | Object detection |
| Classes | 1 (`sheep`) |
| Train images | 3,609 |
| Validation images | 350 |
| Test images | 174 |
| Total images | 4,133 |
| Invalid zero-area annotations removed from processed view | 51 |
| Dataset license | Public Domain, as published by the provider |

Raw files remain unchanged. Preparation creates relative image links, cleaned
labels, a generated `data.yaml`, and a machine-readable preparation report.

## Recorded baseline

The selected checkpoint is `yolo26n-aerial-sheep-v1-best-e10`. Its versioned
manifest is
[`configs/model_yolo26n_aerial_sheep_v1.toml`](../../configs/model_yolo26n_aerial_sheep_v1.toml).

| Metric | Result |
|---|---:|
| Precision | 0.9582 |
| Recall | 0.9341 |
| mAP@50 | 0.9627 |
| mAP@50–95 | 0.5680 |
| Count MAE | 6.276 |
| Count RMSE | 11.390 |
| CPU latency p50 | 31.9 ms |
| CPU latency p95 | 35.5 ms |

## Evaluation limitation

The audit found adjacent frames from at least seven DJI videos in multiple
splits and 221 cross-split image pairs with a 64-bit difference-hash distance of
at most two. Exact file duplicates and exact source IDs do not cross splits, but
the temporal similarity makes random-split validation and test metrics
optimistic.

The recorded results are a technical baseline, not a field guarantee. Precision,
recall, mAP, counting error, latency, and this leakage warning must be reported
together.

## Consequences

- The model is small enough for an interactive local workflow.
- Training and inference use the same image size and class map.
- Dataset preparation is repeatable without modifying the raw export.
- Product-quality claims require a new split grouped by source video or flight,
  retraining, and comparison against manual field counts.

## Follow-up

1. Recover source-video or flight identifiers.
2. Rebuild grouped train, validation, and test splits.
3. Select the operating threshold from validation behavior and business cost.
4. Evaluate the held-out test set once after model selection.
5. Record demo-hardware latency and end-to-end counting error again.

## Related documents

- [ADR 0002: Product scope](0002-product-scope.md)
- [ADR 0003: Runtime and containers](0003-model-runtime-and-containers.md)
- [Main README](../../README.md)

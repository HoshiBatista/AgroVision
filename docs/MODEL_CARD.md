# Model card: YOLO26n Aerial Sheep v1

This model card describes the selected AgroVision baseline checkpoint, its
measured behavior, and the limits on claims that can be made from it.

## Model details

| Field | Value |
|---|---|
| Name | YOLO26n aerial sheep detector |
| Version | `yolo26n-aerial-sheep-v1-best-e10` |
| Architecture | YOLO26 Nano object detector |
| Task | Single-class object detection and visual counting |
| Target class | `sheep` |
| Input size | 640 px |
| Selected epoch | 10 |
| Native artifact | PyTorch `best.pt` |
| Artifact size | 20,740,677 bytes |
| SHA-256 | `29561fa0c96052b9efac892a1dd4a6418508992f4c882b661d08afe5ba124e0d` |
| Inference floor | 0.25 |
| Default operating threshold | 0.40 |
| Training seed | 42 |
| Training device for recorded run | Apple MPS |

The versioned source of truth is
[`configs/model_yolo26n_aerial_sheep_v1.toml`](../configs/model_yolo26n_aerial_sheep_v1.toml).
The runtime verifies the artifact checksum before loading it. The weight file is
not stored in Git.

## Intended use

The model detects sheep in aerial images and short videos, then turns detections
into an estimated flock count, uncertainty signal, annotated evidence, and a
recommended review workflow. It is intended for an offline-capable hackathon
demo, engineering evaluation, and supervised decision support.

It is not validated for unattended livestock inventory, billing, insurance,
regulatory reporting, health or welfare diagnosis, individual identification,
or safety-critical control. A human operator should review uncertain and
high-consequence results.

## Training

The checkpoint was fine-tuned from `yolo26n.pt` using the cleaned YOLO view of
Roboflow `riis/aerial-sheep` version 1. The configured maximum was 50 epochs with
early stopping, batch size 16, image size 640, seed 42, and automatic device
selection. Epoch 10 was selected as the best checkpoint.

Training configuration and entry point:

- [`configs/train_yolo26n_aerial_sheep.toml`](../configs/train_yolo26n_aerial_sheep.toml)
- [`ml/training/train_yolo26.py`](../ml/training/train_yolo26.py)

See the [dataset card](DATASET_CARD.md) for data composition and cleaning.

## Recorded evaluation

| Metric | Result |
|---|---:|
| Precision | 0.9582 |
| Recall | 0.9341 |
| mAP@50 | 0.9627 |
| mAP@50-95 | 0.5680 |
| Count MAE | 6.276 sheep |
| Count RMSE | 11.390 sheep |
| CPU inference latency p50 | 31.9 ms |
| CPU inference latency p95 | 35.5 ms |

These values were measured on the provider test split. Adjacent DJI video frames
cross train, validation, and test splits, and 221 near-duplicate cross-split
pairs were found. The metrics are therefore optimistic and are a reproducible
technical baseline, not an independent field-performance guarantee. Hardware,
preprocessing, concurrency, encoding, and end-to-end video work can also make
application latency higher than detector-only latency.

## Output and counting semantics

The runtime returns a label, confidence, absolute-pixel bounding box, and
confidence classification for each detection. Detections at or above 0.40 are
included in the default confident count. Detections from 0.25 up to 0.40 are
surfaced as uncertain for operator review. Values below 0.25 are not returned by
the detector.

For video, frame counts are sampled into a time series. The summary reports the
maximum count, mean count, and timestamp of the peak; it does not track animal
identity across frames and must not be interpreted as the number of unique sheep
that crossed the camera view.

The operating threshold is runtime-configurable from 0.25 through 0.95. A
threshold change is process-local metadata, not a newly evaluated model release.

## Limitations and failure modes

- Dense flocks and overlapping animals can cause missed detections.
- Shadows, vegetation, rocks, and compression artifacts can cause false
  positives.
- Altitude, motion blur, oblique views, small objects, and unfamiliar cameras
  can reduce recall.
- Adjacent-frame leakage limits confidence in the published baseline.
- Dataset coverage is not demonstrated across farms, regions, seasons, breeds,
  weather, or thermal imagery.
- Single-frame detection does not reconcile duplicate animals across time.
- The model predicts only `sheep`; it cannot infer identity, health, sex, weight,
  or ownership.

The application should surface the model version, threshold, uncertain count,
and these limitations near decisions based on the output.

## Runtime controls

- The checksum and configured version bind runtime output to the reviewed
  artifact.
- Model loading occurs once during application startup.
- A bounded queue serializes access to the detector and returns explicit busy or
  timeout errors under load.
- Upload byte limits, image pixel limits, media validation, and processed-frame
  limits bound input work.
- The native checkpoint is the tested runtime. Any portable export requires its
  own parity and performance validation before replacing it.

## Reproduction and release gate

```bash
make prepare
make train
make evaluate
make model-checksum
```

Training is stochastic and hardware-dependent even with a fixed seed. Record the
code revision, dependency lock, dataset version, configuration, device,
wall-clock duration, selected epoch, and generated evaluation report for every
candidate.

A successor may replace this baseline only after it has:

1. a unique model version and immutable artifact hash;
2. evaluation on a leakage-safe, source-grouped split;
3. per-class detection metrics, count error, and p50/p95 latency;
4. threshold selection from validation behavior and operating cost;
5. regression coverage through the API and web workflow;
6. a documented rollback path.

See [ADR 0001](adr/0001-aerial-sheep-baseline.md),
[ADR 0003](adr/0003-model-runtime-and-containers.md), and the
[operations runbook](OPERATIONS.md).

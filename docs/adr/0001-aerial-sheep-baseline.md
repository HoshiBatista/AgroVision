# ADR 0001: aerial sheep detection baseline

- Status: accepted
- Date: 2026-09-12

## Decision

Train `yolo26n.pt` at 640 px on Roboflow `riis/aerial-sheep` version 1, exported
as YOLO11 detection labels. The task has one class, `sheep`. Version 1 contains
4,133 generated images: 3,609 train, 350 validation, and 174 test.

The raw export is immutable. Preparation removes 51 zero-area annotations from a
generated label view before training. The model trains for at most 50 epochs with
early stopping, batch size 16, a fixed seed, and Apple MPS on the current machine.

## Evaluation limitation

The downloaded split contains adjacent frames from at least seven DJI videos in
train, validation, and test. An audit also found 221 cross-split image pairs with
a 64-bit difference hash distance of at most two. Exact file duplicates and exact
source IDs do not cross splits, but the temporal leakage makes random-split
validation and test metrics optimistic.

This run is a technical baseline. Product-quality claims require rebuilding the
split by source video or flight and retraining. Report mAP50-95, precision,
recall, count MAE/RMSE, latency, and this limitation together.

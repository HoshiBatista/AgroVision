---
name: ML or dataset change
about: Propose a dataset, training, evaluation, threshold, or model update
title: "[ML/Data] "
labels: ml,data
assignees: ""
---

## Hypothesis

State one measurable change and why it should improve the product workflow.

## Dataset provenance

- Source and owner:
- Exact version and acquisition date:
- Task and class map:
- License and attribution:
- Immutable raw location:
- Grouping key for train/validation/test:

Do not attach raw datasets, private media, provider tokens, or download URLs that
contain credentials.

## Experiment

- Baseline model/version:
- Configuration change:
- Seed, code revision, environment, and hardware:
- Training budget and stopping rule:
- Threshold-selection method:

## Evaluation plan

Include per-class precision/recall, mAP50-95, count MAE/RMSE, error analysis,
artifact size, p50/p95 latency, and end-to-end workflow behavior. Keep the held-out
test split sealed until model and threshold selection are complete.

## Leakage and representativeness

Describe duplicate checks, grouping, source overlap, subgroup gaps, field-data
coverage, and how known limitations will be reported.

## Release and rollback

- New dataset/model version:
- Artifact checksum and storage:
- API/UI compatibility:
- Regression tests:
- Rollback artifact and trigger:
- Required dataset card, model card, changelog, and ADR updates:

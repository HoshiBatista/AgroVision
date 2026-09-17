# AgroVision roadmap

This roadmap orders work by evidence and operational risk. It is not a delivery
date commitment. Items move to complete only when their stated evidence exists
in the repository or a linked release record.

## Current baseline

The repository already provides a coherent local path from a versioned dataset
through preparation, training, evaluation, a checksum-bound model runtime,
FastAPI, a React interface, stream simulation, authentication, journal exports,
tests, Docker Compose, and CI.

The baseline remains an engineering and hackathon demonstration. Known temporal
leakage in the supplied dataset prevents production or independent field
performance claims.

## P0: trustworthy evaluation

Goal: replace optimistic benchmark evidence with a defensible estimate of the
actual operating workflow.

- recover source-video, flight, farm, or capture-session identifiers;
- create versioned grouped train, validation, and test splits;
- rerun annotation, corruption, duplicate, and near-duplicate audits;
- retrain the fixed baseline before changing architecture or augmentation;
- select the confidence threshold from validation behavior and the cost of
  misses versus duplicate counts;
- evaluate the held-out test split once after selection;
- compare image and video estimates with manual field counts;
- report mAP50-95, per-class precision/recall, count MAE/RMSE, error examples,
  artifact size, and p50/p95 latency on named demo hardware.

Exit evidence: a new dataset manifest and card, model card, reproducible run
metadata, grouped-split audit, evaluation report, and reviewed release decision.

## P1: product reliability

Goal: make the end-to-end operator path predictable under realistic load and
recoverable failure.

- add concurrency and soak tests for the bounded inference queue;
- establish image/video size budgets from measurements on target hardware;
- test RTSP disconnect, timeout, reconnect, and corrupt-frame behavior;
- add browser-level tests for login, upload, results, history, and export;
- harden client token storage and session-expiry behavior;
- measure end-to-end latency separately from detector latency;
- add structured operational metrics and actionable readiness reasons;
- define upload retention and cleanup with tests;
- exercise database backup and restore in an isolated environment.

Exit evidence: recorded load envelope, automated critical-path tests, recovery
drill, retention policy, and observable service-level indicators.

## P2: deployment hardening

Goal: support a controlled shared pilot without silently expanding model claims.

- terminate TLS at a maintained reverse proxy;
- use managed secrets and rotation instead of local environment files;
- isolate PostgreSQL and storage from public ingress;
- pin and scan container images and dependencies;
- add release provenance for application, migrations, model, and configuration;
- automate backup verification and documented rollback checks;
- define access, audit, data-retention, and incident-response ownership;
- run privacy and threat reviews for real aerial imagery and RTSP sources.

Exit evidence: deployment review, successful restore and rollback drills,
security checklist, vulnerability response path, and pilot approval with explicit
scope.

## P3: measured model and edge improvements

Goal: improve cost or decision quality only after the baseline is trustworthy.

- compare portable model exports with the native checkpoint for parity, latency,
  and size;
- profile representative edge hardware before selecting an export/runtime;
- improve small-object and dense-flock behavior using one controlled change at a
  time;
- add drift and difficult-example review based on consented field data;
- consider a second model only when it consumes or enriches the first model's
  output in one operator workflow and improves an end-to-end metric;
- write a new ADR before adopting any second model or major framework change.

Exit evidence: reproducible experiments, independent metrics per model, combined
workflow evaluation, resource profile, and rollback for every artifact.

## Explicit non-goals

- distributed services, task queues, Kubernetes, feature stores, or cloud-only
  inference without a measured need;
- animal identity, health, weight, or welfare claims from the current detector;
- threshold tuning on the held-out test set;
- hiding dataset leakage behind aggregate metrics;
- adding a decorative second model to satisfy presentation optics;
- calling the system production-ready before field, security, load, recovery,
  and operational evidence exists.

## Prioritization rule

When choosing the next item, prefer the smallest vertical change that reduces the
largest unmeasured product risk. Update the [changelog](../CHANGELOG.md), relevant
ADR, [dataset card](DATASET_CARD.md), [model card](MODEL_CARD.md), and
[operations runbook](OPERATIONS.md) whenever the evidence or operating contract
changes.

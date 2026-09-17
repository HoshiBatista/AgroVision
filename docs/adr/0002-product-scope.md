# ADR 0002: product scope — aerial sheep detection and counting web product

- Status: accepted
- Date: 2026-09-12
- Supersedes discovery in `docs/PROJECT_IDEAS.md` (topic selection is now fixed)

## Context

`docs/PROJECT_IDEAS.md` enumerated several candidate two-model concepts and was
explicitly a discovery document. A product topic must be selected and captured
here before building the application layer, per `CLAUDE.md`.

The team selected the aerial-sheep direction that already has a trained baseline
(`docs/adr/0001-aerial-sheep-baseline.md`): detect and count sheep in aerial
drone imagery with YOLO26n. The product is an operational monitoring tool for a
livestock operator, not a meat-quality pipeline.

## Decision

Build **AgroVision**, an end-to-end web product for aerial sheep monitoring.

### Primary user and decision
A **livestock operator / farm monitor** who needs to know *how many sheep are
present* across drone footage and still imagery, watch multiple drone feeds at
once, and export a defensible count report. The core decision the product
supports: "is the counted flock size on this feed within expectation, and which
feed needs a human to look now?"

### Model roles
This product ships a **single detection model** (YOLO26n, one class `sheep`) used
in three surfaces that share one application use case:
1. single-image detection and count;
2. uploaded-video detection with a per-frame count time series;
3. simulated live drone streams feeding an aggregate dashboard.

The two-model cascade described for other concepts in `PROJECT_IDEAS.md` is **out
of scope** for this product. If a second model is added later (e.g. flock
health/behavior on detected crops), it will be recorded in a new ADR. The
`AGENTS.md` two-model guidance is a default, not a hard requirement, and is
consciously narrowed here in favor of one workflow that works reliably.

### Deviations from `AGENTS.md` defaults
Both are intentional and scoped:

1. **UI stack: React (Vite) + TypeScript + Tailwind instead of Streamlit.**
   The product requires a polished marketing landing page (animated clouds and
   sheep), a real authentication flow, a multi-tile live-stream dashboard, and
   MJPEG video tiles. Streamlit cannot deliver this presentation quality or the
   streaming layout. The web app still calls the exact same versioned API /
   application use cases as any other client, preserving the `AGENTS.md`
   contract that UI and API share one path.

2. **Primary database: PostgreSQL instead of SQLite.**
   Full JWT auth (registration, login, refresh, roles) and a session journal are
   in scope. Postgres runs locally via `docker-compose` and needs no paid cloud
   service, so the offline-after-setup requirement still holds. Persistence stays
   behind a repository port, so SQLite remains a possible swap without touching
   domain logic.

## Scope

In scope (MVP, all required for the defense):
- landing page, JWT registration/login;
- single-photo inference with annotated result and count;
- single-video inference with annotated output and count time series;
- simulated live drone streams (from files) with an aggregate dashboard
  (per-stream counts, trends, latency);
- CSV/PDF report export and a session journal.

Out of scope for MVP: a second cascade model; real RTSP/RTMP ingestion (the
stream source is abstracted so it can be added later); multi-tenant org
management; mobile apps.

## Limitations to surface in the UI

- Counts are a **visual estimate**. Occlusion, flock density, flight altitude,
  motion blur, and small object size cause miss/double counts. The UI must show
  the model version and mark low-confidence detections as uncertain.
- The baseline split has documented temporal leakage (see ADR 0001), so reported
  validation/test metrics are optimistic until the split is rebuilt by
  source video/flight. `GET /v1/model-info` and the evaluation report must carry
  this caveat.

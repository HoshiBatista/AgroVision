# ADR 0002: Aerial sheep detection and counting product

| Field | Value |
|---|---|
| Status | Accepted with implementation notes |
| Date | 2026-09-12 |
| Owners | AgroVision team |
| Decision area | Product scope and application architecture |
| Supersedes | [`docs/PROJECT_IDEAS.md`](../PROJECT_IDEAS.md) as active direction |

## Context

The discovery phase compared several agribusiness concepts, including two-model
cascades. A hackathon implementation needed one coherent user, one operational
decision, an end-to-end path from data to application, and a reliable offline
demo.

The aerial-sheep baseline in [ADR 0001](0001-aerial-sheep-baseline.md) was already
measured and could support a narrower, more credible workflow than starting two
unrelated models.

## Decision

Build **AgroVision**, a locally controlled product for detecting and counting
sheep in aerial images and video.

### Primary user

The primary user is a livestock operator or farm monitor who needs to answer:

> Is the visible flock size within expectation, and which source needs human
> review now?

### Model scope

Ship one YOLO26n detector with one class, `sheep`. The same application-level
inference path supports:

1. uploaded-image detection and counting;
2. uploaded-video analysis with a count time series;
3. file-backed drone streams on an aggregate dashboard;
4. dynamically connected RTSP streams.

A second model is not decorative scope. It may be added only if it consumes the
detector output or completes a measured lifecycle decision, and it requires a
new ADR plus end-to-end evaluation.

### Product outcome

Each inference surface must provide more than bounding boxes:

- a confident count and visible uncertain detections;
- model version, threshold, limitations, and processing time;
- an annotated result suitable for review;
- a session record and exportable report when the user is authenticated;
- one versioned API contract shared by the web application.

## Architecture choices

### React instead of Streamlit

Use React, TypeScript, Vite, and Tailwind for the web client. The product requires
a polished landing page, authentication, multiple live tiles, MJPEG playback,
responsive controls, and a dashboard that would be awkward to express in the
default Streamlit stack.

The React client remains a thin API consumer. Business rules stay in domain and
application layers.

### Dual local database modes

Keep persistence behind repository ports. SQLite is the zero-service default for
local setup and offline demonstration. PostgreSQL is the containerized integration
and deployment profile used for real repository tests, concurrent sessions, and
the full Docker stack.

## Delivered scope

| Capability | Initial MVP decision | Current implementation |
|---|---|---|
| Landing page and Russian UI | In scope | Delivered |
| JWT registration and login | In scope | Delivered |
| Image inference | In scope | Delivered |
| Video inference and time series | In scope | Delivered |
| File-backed drone dashboard | In scope | Delivered |
| Session journal and CSV/PDF export | In scope | Delivered |
| RTSP ingestion | Initially deferred | Delivered through `StreamSourcePort` |
| Multi-tenant organization management | Out of scope | Not implemented |
| Native mobile applications | Out of scope | Not implemented |
| Second model | Out of scope | Not implemented |

## Implementation notes

RTSP support was added after the initial MVP scope without changing domain rules:
the existing stream port gained a concrete RTSP adapter, reconnect behavior, and
server-side URI handling. SQLite became the default local mode while PostgreSQL
remained the full integration and Docker mode. These are implementation refinements
within the accepted modular-monolith boundary.

## Consequences

- One model can be versioned, evaluated, and rolled back independently.
- Every user-facing inference path shares the same model metadata and threshold.
- The demo works locally without a paid inference service.
- React adds a separate Node.js toolchain, lockfile, and CI job.
- Two database modes require contract tests and real PostgreSQL integration tests.

## Product limitations

- Counts are visual estimates, not inventory guarantees.
- Occlusion, density, altitude, blur, shadows, and small objects affect accuracy.
- Low-confidence detections must remain visible as uncertain outcomes.
- Baseline metrics are optimistic because of the temporal split leakage described
  in ADR 0001.
- The product has not yet been validated as a production livestock system.

## Related documents

- [ADR 0001: Dataset and baseline](0001-aerial-sheep-baseline.md)
- [ADR 0003: Runtime and containers](0003-model-runtime-and-containers.md)
- [Archived discovery](../PROJECT_IDEAS.md)
- [Main README](../../README.md)

# AgroVision architecture

AgroVision is a modular monolith: one product deployable as a small local stack,
with explicit internal boundaries around domain rules, use cases, adapters, and
presentation. The design keeps the inference path reproducible and avoids the
operational cost of distributed services before measurements justify them.

## System context

An operator uses the React web client or the versioned API to submit an image,
video, or RTSP source. FastAPI validates the request and invokes application use
cases. A locally controlled YOLO detector produces detections; application logic
turns those detections into confident and uncertain counts. PostgreSQL or SQLite
stores users and journal records, while local object storage holds uploaded and
annotated media.

```text
Operator
   |
   +-- React web client --------+
   |                            |
   +-- API client --------------+--> FastAPI presentation
                                      |
                                      v
                                Application use cases
                                  |             |
                                  v             v
                              YOLO adapter   Repository ports
                                  |             |
                                  v             v
                            Model artifact   SQLite/PostgreSQL
                                  |
                                  v
                           Annotated media
```

The web client and external clients consume the same HTTP contracts. The API and
stream workers share the same detector instance and bounded inference queue.

## Repository boundaries

| Area | Responsibility | Dependency rule |
|---|---|---|
| `src/agrovision/domain` | Entities, value objects, counting and report rules | Imports no frameworks or adapters |
| `src/agrovision/application` | Use cases and the ports they consume | Depends on domain, not FastAPI/SQLAlchemy/YOLO |
| `src/agrovision/infrastructure` | Model, database, storage, security, reporting, and streaming adapters | Implements application ports |
| `src/agrovision/presentation` | Transport schemas and presenters | Maps domain/application results to stable contracts |
| `apps/api` | Composition root, dependencies, middleware, and thin routes | Wires all server-side boundaries |
| `apps/web` | Operator-facing React and TypeScript client | Calls the versioned API |
| `ml` | Dataset preparation, training, and evaluation | Uses versioned configuration and writes ignored artifacts |
| `configs` | Non-secret model, training, and stream configuration | Reviewed source of concrete defaults |
| `tests` | Unit, contract, integration, and smoke evidence | Protects behavior at each boundary |

Dependencies point inward. Interfaces are declared at the boundary that needs
them, and runtime dependencies are passed explicitly. A framework type must not
leak into the domain layer.

## Image request flow

1. Middleware assigns or preserves `X-Request-ID`.
2. The route enforces the declared media type and upload byte limit.
3. The image adapter decodes bytes and enforces the pixel limit.
4. The use case submits work to the bounded detector queue outside the async event
   loop.
5. The detector preprocesses at the configured image size and filters the target
   class above the inference floor.
6. Domain/application logic separates confident and uncertain detections using
   the operating threshold.
7. Infrastructure annotates the result; the presenter creates the stable API
   response.
8. If the request is authenticated, a summary is written to that user's journal.

Video inference uses the same detector contract frame by frame, stores an
annotated output, and returns time-series samples and keyframes. Stream workers
also reuse the detector and publish their latest metrics to the dashboard bus.

## Model lifecycle

The model path, version, SHA-256, class, image size, inference floor, and default
threshold are explicit configuration. The application loads the model once
during startup, verifies integrity, and does not become ready if the required
artifact cannot be trusted.

One detector instance is shared because model runtimes are expensive and are not
assumed to be safely concurrent. A bounded queue serializes calls and applies a
queue wait plus execution timeout. Overload produces stable `503` or `504`
responses instead of unbounded work.

The runtime threshold can be changed by an authenticated user. This affects all
entry points in the current process but does not mutate the model artifact or
create a new evaluated model release.

## Data and persistence

Repository ports isolate persistence from application logic. SQLite supports the
offline local workflow; PostgreSQL supports Docker and CI without changing use
cases. Alembic owns schema evolution.

Authentication uses Argon2 password hashes and signed access/refresh tokens.
Journal queries are scoped to the authenticated user. Media storage is separate
from relational records and is configured through an explicit storage root.

The raw ML dataset is immutable and ignored by Git. Preparation creates a
separate cleaned view; training and evaluation write versioned, ignored artifacts.
Metadata needed to identify a selected model remains tracked in configuration and
the model card.

## Process lifecycle

FastAPI's lifespan is the composition boundary:

1. validate settings;
2. build and verify the detector;
3. create the password and token services;
4. create the database engine and session factory;
5. create and start the stream manager;
6. serve requests only after startup succeeds;
7. stop stream workers, close the detector queue, and dispose the database engine
   during shutdown.

Tests inject fake detectors and stream managers through the same composition
root, avoiding model loads while preserving real HTTP contracts.

## Deployment shape

The default local path runs the API and web client with SQLite. Docker Compose
runs the web proxy, API, and PostgreSQL as one bounded stack. The database and API
ports bind to loopback in the provided profile; the web proxy is the user-facing
entry point.

This is intentionally not a microservice architecture. Any task queue, cloud
database, separate inference service, or orchestration platform requires measured
capacity or reliability evidence and a new architecture decision record.

## Cross-cutting controls

- settings are environment-driven and validated at startup;
- secrets, datasets, model weights, uploads, and generated predictions stay out
  of Git;
- stable errors avoid exposing stack traces to clients;
- request IDs support correlation without logging raw imagery or tokens;
- checksums bind the reviewed model metadata to its local artifact;
- byte, pixel, frame, queue, and timeout limits bound expensive work;
- API schemas and versioning protect clients from accidental contract changes.

## Decision records and further detail

- [ADR 0001](adr/0001-aerial-sheep-baseline.md): dataset, baseline, and leakage
- [ADR 0002](adr/0002-product-scope.md): product workflow and modular-monolith scope
- [ADR 0003](adr/0003-model-runtime-and-containers.md): model integrity, queue, and containers
- [API reference](API.md): transport contracts
- [Dataset card](DATASET_CARD.md) and [model card](MODEL_CARD.md): ML evidence
- [Operations runbook](OPERATIONS.md): startup, recovery, and rollback

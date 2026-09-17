# ADR 0003: Model artifact, inference queue, and containers

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-09-12 |
| Owners | AgroVision team |
| Decision area | Runtime safety and deployment |

## Context

HTTP image requests, uploaded-video analysis, and live stream workers share one
mutable Ultralytics model. Concurrent calls from asyncio handlers and worker
threads are unsafe, while synchronous inference inside an async route blocks
unrelated requests.

A reproducible deployment must also reject a missing, corrupt, or substituted
checkpoint instead of silently loading a generic COCO model.

## Decision

### Selected artifact

Use the checkpoint `yolo26n-aerial-sheep-v1-best-e10` with SHA-256:

```text
29561fa0c96052b9efac892a1dd4a6418508992f4c882b661d08afe5ba124e0d
```

The versioned metadata lives in
[`configs/model_yolo26n_aerial_sheep_v1.toml`](../../configs/model_yolo26n_aerial_sheep_v1.toml).
At startup the adapter verifies the digest and the target `sheep` class before
serving traffic.

Generic fallback is disabled by default. If an operator explicitly enables it,
inference is filtered to the COCO `sheep` class and the fallback status appears
in model limitations.

### Inference serialization

Route every detector call through a bounded, single-worker inference queue.
Image and video use cases execute model work in worker threads, keeping the
asyncio event loop free. Stream workers share the same queued detector, so model
access remains serialized across every entry point.

Queue capacity, wait time, and inference timeout are validated environment
settings. Overload produces an explicit application error rather than unbounded
memory growth.

### Device policy

`MODEL_DEVICE=auto` chooses CUDA, then Apple MPS, then CPU. Local configuration
may pin a device. The Linux API container uses CPU because Apple MPS is not
available inside Docker.

### Container topology

Docker Compose provides three services:

```text
Browser -> Nginx and React -> FastAPI -> PostgreSQL 16
                              |
                              +-> read-only model and demo media
```

The API runs as uid `10001`. Model weights and demo inputs are mounted read-only;
uploads and PostgreSQL data use named volumes. Database health gates API startup,
and API readiness gates the web service.

## Consequences

### Positive

- Wrong or modified weights fail at startup with an actionable error.
- One queue protects the detector and provides predictable backpressure.
- Long-running inference does not block FastAPI's event loop.
- Native local execution and CPU containers use the same application boundary.
- Model provenance and fallback state are visible to users.

### Trade-offs

- A single worker limits per-process inference throughput.
- Long videos still occupy model capacity and must obey processed-frame limits.
- Horizontal scale requires multiple API instances, each with its own model copy.
- The model artifact remains outside Git and must be provisioned before startup.

## Operational checks

- `GET /health` verifies process health.
- `GET /ready` verifies that the detector is loaded.
- The configured checksum must match before the application becomes ready.
- CI validates Docker Compose but does not download or execute private model
  artifacts.

## Related documents

- [ADR 0001: Dataset and baseline](0001-aerial-sheep-baseline.md)
- [ADR 0002: Product scope](0002-product-scope.md)
- [Docker Compose configuration](../../docker-compose.yml)
- [Main README](../../README.md)

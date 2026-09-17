# ADR 0003: selected model artifact, inference queue, and containers

- Status: accepted
- Date: 2026-09-12

## Context

The application, uploaded-video analyzer, and simulated streams share one mutable
Ultralytics model. Calling it concurrently from asyncio handlers and worker threads
is unsafe, while running synchronous inference directly inside an async route blocks
unrelated requests. A clean deployment must also reject missing or substituted model
weights instead of silently loading a generic COCO detector.

## Decision

The selected artifact is `yolo26n-aerial-sheep-v1-best-e10`, with SHA-256
`29561fa0c96052b9efac892a1dd4a6418508992f4c882b661d08afe5ba124e0d`.
The versioned model manifest is `configs/model_yolo26n_aerial_sheep_v1.toml`.

At startup the adapter verifies the digest and target `sheep` class before serving
traffic. Generic fallback is disabled unless an operator explicitly enables it; even
then, inference is filtered to the COCO `sheep` class and the fallback status appears
in model limitations.

All detector calls pass through a bounded, one-worker inference queue. API handlers
run image and video use cases in worker threads, keeping the asyncio event loop free.
Stream workers use the same queued detector, so access remains serialized across all
entry points.

The local device remains configurable. `auto` chooses CUDA, then Apple MPS, then CPU;
the generated local configuration may pin MPS. The Linux API container explicitly
uses CPU. Docker Compose builds the API and web images, runs PostgreSQL, mounts the
selected weights and demo videos read-only, and persists uploads in a named volume.

## Consequences

- A corrupt or wrong checkpoint fails at startup with an actionable error.
- Queue capacity and deadlines provide predictable overload behavior.
- Long videos no longer block FastAPI's event loop, but they still consume model
  capacity and should remain bounded by the configured processed-frame limit.
- The model artifact stays outside Git and must be supplied before container startup.

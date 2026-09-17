# Agent Working Agreement

This file is the canonical instruction set for every coding agent working in this
repository. Tool-specific instruction files must point here and must not redefine
the architecture independently.

## Mission

Build a polished, reproducible, end-to-end Python product for an agribusiness
hackathon. The result must solve a concrete operational problem and demonstrate
the full path from a versioned dataset through model training and evaluation to a
usable application.

The selected product is YOLO26 Nano detection and counting on Roboflow
`riis/aerial-sheep` version 1. Preserve the raw export and record the known
video-frame split leakage when reporting metrics. The accepted MVP scope uses
one model; ADR 0002 governs any later decision to add a second model.

## Communication

- Speak with the user in Russian unless they ask for another language.
- Keep code, identifiers, commit messages, logs, and technical documentation in
  English. Product UI copy should be Russian by default.
- Lead with outcomes and evidence. State assumptions and material trade-offs.
- Do not call a prototype production-ready without measured evidence.

## Product standard

The demo must tell one coherent story:

1. A user supplies a real image, a batch, or a short video.
2. The application validates and processes the input.
3. A locally controlled model returns predictions with confidence values.
4. The product turns predictions into a useful agribusiness action, not only
   colored boxes or a class name.
5. The UI shows the model version, limitations, and enough result detail to earn
   trust.
6. The same inference path is accessible through a versioned API.

The two-model design must be functional rather than decorative. Prefer a cascade
where model A creates regions or context consumed by model B. If the models serve
two stations in a lifecycle, the UI must connect them through one user role,
record, and decision. Report each model's metrics separately and measure the
combined workflow end to end.

Prefer a narrow workflow that works reliably over a broad set of unfinished
features. The happy path must run without paid cloud services. External tracking
and deployment services may be optional adapters.

## Architecture

Use a modular monolith with explicit boundaries. Start with this layout and
change it only through a short architecture decision record:

```text
apps/
  api/                 # FastAPI composition and HTTP routes
  web/                 # Python UI, normally Streamlit
src/agrovision/
  domain/              # Entities, value objects, domain rules; no frameworks
  application/         # Use cases and ports (Protocols)
  infrastructure/      # Model, storage, telemetry, and external adapters
  presentation/        # API/UI schemas and presenters
ml/
  data/                # Dataset validation and preparation code
  training/            # Training pipelines
  evaluation/          # Metrics, error analysis, and reports
configs/               # Versioned non-secret YAML/TOML configuration
tests/                  # Unit, integration, contract, and smoke tests
scripts/               # Thin repeatable entry points
artifacts/              # Generated models/reports; ignored by Git
docs/adr/               # Architecture and product decisions
```

Dependencies point inward: presentation and infrastructure may depend on
application and domain; domain must not import FastAPI, Streamlit, SQLAlchemy,
Roboflow, or a model framework. Put interfaces at the boundary that consumes
them. Keep route handlers and UI callbacks thin.

Pass typed settings and dependencies explicitly. Avoid global mutable state and
hidden singleton clients. Give each model its own inference port and metadata,
then compose them in an application-level pipeline. Load models once during
application startup. Do not load model weights per request.

## Technology defaults

- Python 3.12, managed with `uv` and a locked dependency set.
- FastAPI and Pydantic v2 for the API.
- Streamlit for the hackathon UI unless interaction requirements justify another
  Python framework.
- PyTorch plus an ADR-selected detection/classification package for training.
- Pillow/OpenCV behind infrastructure adapters for image handling.
- SQLite for a self-contained demo; keep persistence behind a repository port so
  PostgreSQL can replace it without changing domain logic.
- `pytest`, `ruff`, and `mypy` for verification.
- Structured logging with request/correlation IDs. Never log raw images, tokens,
  or personal metadata by default.

Do not add a distributed system, task queue, Kubernetes, feature store, or cloud
database unless measured requirements demand it.

## Data and ML rules

- Use a dataset only after recording its source URL, owner, exact version, task,
  class map, size, license, download date, and required attribution.
- Keep raw data immutable. Never commit datasets, weights, caches, or generated
  predictions to Git.
- Store dataset and model metadata in versioned manifests; store large files
  outside Git or through an explicitly configured artifact mechanism.
- Audit annotations before training: class counts, empty labels, corrupt files,
  duplicate or near-duplicate images, box validity, and representative samples.
- Split by original scene, video, farm, plant, or capture session when possible.
  Never let augmented variants or adjacent video frames cross data splits.
- Fix random seeds and record code revision, configuration, dataset version,
  environment, hardware, and wall-clock duration for every reported run.
- Establish a small baseline first. Change one meaningful factor at a time.
- Evaluate on a held-out test set only after model selection. For detection,
  report at least mAP50-95, per-class precision/recall, confusion/error examples,
  model size, and p50/p95 inference latency on the demo hardware. For
  classification, report macro F1 and per-class recall in addition to accuracy.
- Choose decision thresholds from validation behavior and product cost, not from
  the test set. Surface low-confidence outcomes as uncertain.
- Keep preprocessing identical in training and inference through shared,
  testable code or exported model metadata.
- Export a portable model when practical and preserve a tested native fallback.
- Treat public pretrained-model metrics as orientation only. Reproduce results on
  our own split before using them in the presentation.
- Version, evaluate, and roll back the two models independently. Add an end-to-end
  evaluation for error propagation through their combined pipeline.

Roboflow may be used to discover and export open datasets. Training and the final
demo must remain reproducible from repository commands and must not silently
depend on a hosted inference endpoint.

## API and UI contract

The initial API should include:

- `GET /health` for process health;
- `GET /ready` for model readiness;
- `GET /v1/model-info` for both versions, class maps, thresholds, and limitations;
- `POST /v1/predictions` for validated inference.

Return stable error bodies, a request ID, model version, confidence, and processing
time. Enforce file size, media type, pixel-count, and request-time limits. Strip
unsafe filenames and image metadata. Never trust an uploaded extension.

The web application must call the same application use case as the API. It must
show a useful empty state, progress, recoverable errors, an annotated result,
structured findings, recommended next action, and an exportable summary. Do not
expose stack traces or implementation details to users.

## Configuration and secrets

- Configuration is environment-driven and validated on startup.
- `.env.example` documents variable names with safe placeholders.
- `.env` and secret files are local-only. Never print, quote, copy, overwrite, or
  commit their values. The existing `.env` belongs to the user.
- Fail with a clear message when required settings are absent. Do not bake API
  keys, absolute machine paths, dataset URLs containing tokens, or credentials
  into code, notebooks, logs, or model metadata.

## Engineering workflow

Before editing, inspect the repository, current diff, relevant instructions, and
tests. Preserve user changes and keep edits scoped to the task.

Expose routine work through stable commands (prefer a `Makefile` backed by small
scripts): `setup`, `lint`, `typecheck`, `test`, `data`, `train`, `evaluate`, `serve`,
and `demo`. Commands must be non-interactive, configuration-driven, and safe to
rerun. Network-dependent steps must be explicit.

Use notebooks only for exploration. Move reusable code into `src/` or `ml/`.
Do not hide core logic in notebooks or shell scripts. Avoid broad exception
handlers, untyped dictionaries at boundaries, and speculative abstractions.

For each change:

1. Implement the smallest complete vertical slice.
2. Add tests that protect meaningful behavior and contracts.
3. Run the focused checks, then the repository verification commands.
4. Update relevant documentation and configuration examples.
5. Report what changed, what passed, and any real limitation that remains.

## Definition of done

A feature is done when it works through the real user path, has typed boundaries,
handles expected failures, has proportionate automated coverage, passes lint and
tests, and can be reproduced from documented commands on a clean checkout.

The hackathon project is done when a clean machine can set it up, obtain the
documented dataset, reproduce the selected model or use a clearly versioned
artifact, launch API and UI, complete the demo without network access after setup,
and view an evaluation report that supports the claims made to judges.

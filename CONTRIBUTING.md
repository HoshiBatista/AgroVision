# Contributing to AgroVision

Thank you for improving AgroVision. This project values small, reproducible
changes that strengthen the complete path from data and model evidence to the
operator-facing product.

Read the following before editing:

1. [`AGENTS.md`](AGENTS.md), the canonical engineering agreement;
2. the relevant accepted [architecture decisions](docs/README.md#architecture-decisions);
3. the [security policy](SECURITY.md) for secrets and vulnerability handling.

## Development setup

Requirements are Python 3.12, `uv`, Node.js 22, npm, and FFmpeg. Docker is
required for the PostgreSQL integration profile.

```bash
make setup
make web-setup
make configure
make migrate
```

Model weights, datasets, `.env`, uploads, and generated predictions are local
artifacts and must not be committed.

## Change workflow

1. Start from an up-to-date `main` branch.
2. Define one bounded outcome and identify the affected architectural boundary.
3. Add or update tests before widening the implementation.
4. Keep domain code free of framework and infrastructure imports.
5. Run focused tests, then the complete verification commands.
6. Update configuration examples, documentation, and ADRs when behavior changes.
7. Submit a reviewable pull request using the repository template.

Suggested branch names:

```text
feature/video-summary-export
fix/inference-timeout-response
docs/model-card-thresholds
ml/grouped-flight-split
```

Commit messages should be imperative, concise, and written in English:

```text
Add grouped split validation
Fix threshold propagation for streams
Document model rollback procedure
```

## Architecture rules

- Dependencies point inward: `presentation` and `infrastructure` may depend on
  `application` and `domain`, never the reverse.
- Interfaces live at the boundary that consumes them.
- FastAPI routes and React components coordinate work; they do not own domain
  rules.
- Settings and dependencies are explicit. Avoid mutable globals and hidden
  clients.
- The model loads once at startup. Never load weights per request.
- Image, video, and stream inference share the same application contract and
  bounded detector queue.
- A new service, database, framework, or model requires measured justification;
  architectural changes require an ADR.

## Verification

Run the Python quality gates:

```bash
make lint
make typecheck
make test
```

Run the web checks:

```bash
cd apps/web
npm ci
npm run lint
npm run build
```

For real database integration tests, start PostgreSQL and expose a dedicated test
database through `TEST_DATABASE_URL`. Never point the suite at development or
production data because integration fixtures recreate the schema.

```bash
TEST_DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@localhost:5432/agrovision_test' \
uv run pytest tests/integration
```

GitHub Actions runs the same Python and web checks with PostgreSQL 16.

## Testing expectations

| Change | Minimum evidence |
|---|---|
| Domain rule | Focused unit tests, including boundary values |
| Application use case | Unit test with explicit fakes |
| API contract | Request/response and stable-error contract tests |
| Database adapter | PostgreSQL integration test |
| Upload or media path | Valid, malformed, oversized, and unsupported inputs |
| Stream behavior | Worker lifecycle, missing source, and concurrency behavior |
| Web behavior | TypeScript check and production build |
| Model adapter | Metadata, threshold, checksum, class filtering, and failure paths |

Tests should assert product behavior, not implementation details. Do not weaken a
test merely to match an accidental output; first confirm the domain contract.

## Data and model changes

Any dataset or training change must record:

- source, owner, exact version, task, class map, license, and acquisition date;
- immutable raw location and generated processed view;
- annotation audit, duplicate analysis, corrupt files, and split grouping;
- random seed, code revision, configuration, device, duration, and artifact path;
- validation-based threshold selection;
- detection, counting, and latency metrics with hardware context;
- known leakage, subgroup gaps, and field-validation limitations.

Do not commit raw datasets, checkpoints, experiment runs, caches, or generated
predictions. Update the [dataset card](docs/DATASET_CARD.md),
[model card](docs/MODEL_CARD.md), and an ADR when the selected baseline changes.

## Documentation style

- Technical documentation, identifiers, code, and commits are written in English.
- Product UI copy and the Russian README are written in Russian.
- Lead with evidence and operational outcomes.
- Keep measured claims next to their limitations.
- Use relative links for repository files and verify them before review.
- Do not embed secrets, tokens, personal data, private RTSP addresses, or local
  absolute paths.

## Pull request checklist

Before requesting review, confirm that:

- the change is scoped and the reason is clear;
- relevant tests fail before the fix and pass afterward;
- lint, typecheck, tests, and web build pass;
- migrations and configuration changes are documented;
- model and dataset claims are reproducible;
- no secrets or large generated artifacts are staged;
- user-facing limitations remain visible;
- documentation and changelog entries are updated when appropriate.

## License

By contributing, you agree that your original contribution may be distributed
under the repository's [MIT License](LICENSE). Do not submit material you do not
have the right to redistribute.

## Summary

Describe the user or engineering outcome in two or three sentences.

## Why

Explain the problem, evidence, and why this scope is appropriate now.

## Changes

- Change one
- Change two

## Verification

List exact commands and results.

```text
make lint
make typecheck
make test
cd apps/web && npm run lint && npm run build
```

## Risk and rollback

Describe failure modes, compatibility concerns, migrations, model or dataset
impact, and the safest rollback.

## Documentation

List updated README, ADR, API, dataset, model, operations, or changelog entries.

## Checklist

- [ ] The change follows `AGENTS.md` and accepted ADRs.
- [ ] Tests cover meaningful behavior and expected failures.
- [ ] Python lint, formatting, typecheck, and tests pass.
- [ ] Frontend typecheck and production build pass when relevant.
- [ ] PostgreSQL integration tests pass when persistence changes.
- [ ] No secrets, datasets, weights, uploads, caches, or generated predictions are committed.
- [ ] Model metrics include their dataset and limitations.
- [ ] Configuration and `.env.example` are updated when required.
- [ ] User-facing documentation and `CHANGELOG.md` are current.
- [ ] The rollback path is understood.

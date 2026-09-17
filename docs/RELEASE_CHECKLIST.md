# Release checklist

Use this checklist for a tagged application release, model release, or shared
demo deployment. Mark non-applicable items explicitly and link the evidence.

## 1. Scope and provenance

- [ ] Release purpose and user-visible changes are documented.
- [ ] The commit, version, date, and responsible maintainer are recorded.
- [ ] `CHANGELOG.md` contains the release entry and known limitations.
- [ ] Accepted ADRs cover material architecture or product decisions.
- [ ] Licenses and attribution are valid for code, data, weights, and demo media.
- [ ] No secrets, private media, datasets, weights, caches, or generated outputs
      are staged unintentionally.

## 2. Verification

- [ ] `uv lock --check` passes.
- [ ] `make lint` passes.
- [ ] `make typecheck` passes.
- [ ] `make test` passes against PostgreSQL, including integration tests.
- [ ] `npm ci`, `npm run lint`, and `npm run build` pass in `apps/web`.
- [ ] `docker compose config --quiet` passes with safe test credentials.
- [ ] The container stack starts cleanly and reports healthy/readiness status.
- [ ] One image, one short video, login, history, and report export complete
      through the real UI path.

Record commands, environment, and results in the release or pull request. A
local test run that skips PostgreSQL integration tests does not satisfy the
database release gate.

## 3. Data and model evidence

- [ ] Dataset source, owner, exact version, task, classes, license, acquisition
      date, and attribution are recorded.
- [ ] Raw data remain immutable and the preparation report is reproducible.
- [ ] Corrupt inputs, annotation bounds, empty labels, duplicates, and
      near-duplicates were audited.
- [ ] Splits are grouped by source video, flight, farm, or capture session, or
      the known leakage is displayed beside every metric.
- [ ] Training records seed, configuration, code revision, dependency lock,
      hardware, duration, and selected epoch.
- [ ] Evaluation reports mAP50-95, per-class precision/recall, count MAE/RMSE,
      error examples, artifact size, and p50/p95 latency.
- [ ] The operating threshold was selected on validation behavior, not the test
      split.
- [ ] Model card and dataset card match the selected artifact.

## 4. Artifact integrity and compatibility

- [ ] Model version, file size, SHA-256, class map, image size, and thresholds
      match versioned configuration.
- [ ] The runtime refuses a missing or tampered artifact by default.
- [ ] Native inference passes; any portable export has parity evidence and a
      tested fallback.
- [ ] API additions are backward compatible within `/v1`; incompatible changes
      have a migration or new version.
- [ ] Database migrations were exercised from the previous release state.
- [ ] Configuration additions have safe placeholders in `.env.example`.

## 5. Security and operations

- [ ] Production-like environments use unique strong secrets and TLS.
- [ ] Database and storage are not exposed to public ingress.
- [ ] CORS, upload limits, pixel/frame limits, queue bounds, and timeouts match
      the deployment.
- [ ] Dependency and container vulnerability results were reviewed.
- [ ] Logs contain request IDs but no raw media, credentials, tokens, or personal
      metadata.
- [ ] Backup and restore were tested for retained database and media state.
- [ ] Monitoring covers readiness, error rate, latency, queue rejection,
      timeouts, stream reconnects, database availability, and storage.
- [ ] Incident owners and the private security-reporting path are known.

## 6. Rollback and sign-off

- [ ] The previous known-good application, model, configuration, and migration
      state are identifiable.
- [ ] Rollback steps were tested or the remaining risk is explicitly accepted.
- [ ] Post-rollback health, readiness, model metadata, authentication, inference,
      and report queries are defined.
- [ ] Dataset leakage, field-validation status, and unsupported use cases remain
      visible in release notes and the product.
- [ ] Final approver confirms that claims match measured evidence.

The current Aerial Sheep v1 baseline has known temporal split leakage. It can be
released as a reproducible demo baseline, but this checklist does not permit it
to be described as independently field-validated or production-ready.

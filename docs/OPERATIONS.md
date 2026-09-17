# AgroVision operations runbook

This runbook covers reproducible startup, health checks, common failures,
rollback, and demo readiness. It does not claim that the current application has
completed production hardening or field validation.

## Supported operating modes

| Mode | Database | Intended use | Start command |
|---|---|---|---|
| Local | SQLite | Development and offline demo | `make local` |
| Split local | SQLite or PostgreSQL | API/web debugging | `make api`, then `make web` |
| Docker Compose | PostgreSQL 16 | Integrated container test/demo | `make docker-up` |
| CI | PostgreSQL 16 service | Repeatable verification | GitHub Actions |

Python 3.12, `uv`, Node.js/npm, and the selected model artifact are required for
local operation. Docker is required only for the container path or local
PostgreSQL.

## First-time local startup

1. Copy `.env.example` to `.env` and keep the resulting file local.
2. Place the selected checkpoint at the configured path, or prepare data and
   train it locally.
3. Run `make local-init` to install dependencies, configure SQLite, migrate the
   database, seed the demo user, and generate demo predictions.
4. Run `make local` for the coordinated API and web development processes.

The exact setup and model acquisition alternatives are documented in the
[main README](../README.md). Never overwrite an existing `.env`; it belongs to
the operator.

## Container startup

Before a shared or production-like deployment, replace all placeholder
credentials and use a JWT secret of at least 32 characters. Then run:

```bash
make docker-up
docker compose ps
```

The database is not intended to be exposed publicly. Put the API behind TLS and
an authenticated reverse proxy when it is reachable outside a trusted local
network. Consult [`SECURITY.md`](../SECURITY.md) before deployment.

## Health and readiness

```bash
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/ready
curl --fail http://localhost:8000/v1/model-info
```

`/health` confirms that the HTTP process responds. `/ready` confirms model
availability. A service should not receive inference traffic until `ready` and
`model_loaded` are both true. `/v1/model-info` must show the expected model
version, checksum, device, class map, threshold, and limitations.

For authenticated failures, use the `X-Request-ID` response header to correlate
the client event with server logs. Do not put tokens, private media, or RTSP
credentials in diagnostic tickets.

## Configuration that changes behavior

All application settings are environment-driven and validated at startup. The
complete safe template is [`.env.example`](../.env.example). Operationally
important groups are:

- environment, logging, CORS, and API binding;
- database URL and database credentials;
- JWT secret and token lifetimes;
- model path, version, checksum, device, thresholds, queue, and timeouts;
- upload, image-pixel, video-frame, and storage limits;
- stream frame stride, publish rate, JPEG quality, and RTSP timeouts.

Treat the model path, version, and checksum as one release unit. Do not enable
the fallback checkpoint silently in a shared environment because it changes the
model behind the same application deployment.

## Common failure guide

| Symptom | Likely cause | Safe response |
|---|---|---|
| Startup fails before serving | Missing model, hash mismatch, invalid settings, or database unavailable | Read the first startup error; verify path/hash and connectivity without disabling integrity checks |
| `/health` succeeds but `/ready` is false | Model did not finish loading or is unavailable | Remove the instance from inference traffic and inspect startup/model logs |
| `401 unauthorized` | Missing, expired, or invalid access token | Log in or refresh; do not weaken endpoint protection |
| `409 conflict` during registration/stream attach | Email or stream ID already exists | Reuse the existing identity or choose a unique ID |
| `413 payload_too_large` | Upload exceeds configured byte limit | Reduce the input or make a reviewed capacity change |
| `415 unsupported_media_type` | Declared type is unsupported or content cannot decode | Re-encode to a documented format; do not trust only the extension |
| `503 inference_busy` | Bounded detector queue is full | Apply client backoff; reduce concurrency or benchmark before raising capacity |
| `504 inference_timeout` | Queue plus inference exceeded the deadline | Reduce input cost and inspect device/load before changing the timeout |
| Stream remains inactive | Source unreachable, codec issue, or RTSP timeout | Test network reachability and source credentials outside logs; verify codec support |
| Database errors after schema change | Migrations did not run or target URL is wrong | Stop writes, verify `DATABASE_URL`, then run `make migrate` once against the intended database |
| Storage errors | Upload volume missing, full, or not writable | Restore the correct mount/permissions and apply the retention policy |

## Monitoring and capacity

The current baseline provides process logs, request correlation IDs, readiness,
per-result processing time, and live stream count/latency snapshots. It does not
yet provide a production metrics backend, tracing, or alert delivery.

At minimum, an operator should observe request/error rate, p50/p95 end-to-end
latency, queue rejections, inference timeouts, model readiness, stream reconnects,
database availability, and storage utilization. Alert thresholds must come from
a load test on the deployment hardware. Detector-only CPU latency in the model
card is not a capacity estimate for uploads or concurrent video.

## Backup and restore

User accounts and inference journal rows live in the configured database;
uploaded and annotated media live under `STORAGE_ROOT`. Back up both when the
deployment promises history retention.

- For SQLite, stop writers and make a consistent copy of the database file.
- For PostgreSQL, use the platform's supported `pg_dump`/`pg_restore` workflow
  with encrypted storage and restricted credentials.
- Back up the exact model artifact, configuration, checksum, migration revision,
  and application commit with the release.
- Apply a documented retention period to uploads; they can contain sensitive
  location or property imagery.

A backup is not complete until a restore has been tested in an isolated
environment and the restored API, authentication, journal, and model readiness
have been verified. The repository does not currently automate that drill.

## Rollback

1. Stop new inference and database writes if data compatibility is uncertain.
2. Capture the failing application revision, model version, checksum, migration
   revision, request IDs, and timestamps.
3. Redeploy the previous known-good application and its matching model/config.
4. Roll back a database migration only if its migration file explicitly supports
   downgrade and a verified backup exists. Prefer forward repair for data-bearing
   environments.
5. Verify `/health`, `/ready`, `/v1/model-info`, login, one known image, and one
   report query before reopening traffic.

Changing only the model file without its version and checksum is not a valid
rollback.

## Incident checklist

1. Identify impact: API, authentication, inference, streaming, storage, or data.
2. Preserve request IDs and time bounds without copying secrets or raw private
   media into chat or issue trackers.
3. Contain the problem by removing unhealthy instances, disabling the affected
   ingress, or reverting the last known release.
4. Verify artifact integrity and configuration provenance.
5. Recover and validate the complete user path.
6. Record cause, detection gap, remediation, owner, and regression test.
7. Use private security reporting for suspected vulnerabilities or exposure.

## Demo preflight

Before a judged or offline demo:

- run `make lint`, `make typecheck`, and `make test`;
- run the web lint and production build from `apps/web`;
- confirm the expected model checksum and readiness;
- verify one image, one short video, authentication, history, and export;
- verify the demonstration media are local and licensed for use;
- disconnect the network and repeat the happy path if offline operation is a
  claim;
- keep a prerecorded inference clip available as a presentation fallback;
- state the dataset leakage and field-validation limitations aloud.

See the [API reference](API.md), [model card](MODEL_CARD.md), and
[roadmap](ROADMAP.md) for contracts and remaining release gates.

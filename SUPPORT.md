# Support

AgroVision is a hackathon and engineering project, not a commercial support
service or a validated livestock-management system. Community support is best
effort and no response time is guaranteed.

## Before requesting help

1. Read the [English README](README.md) or [Russian README](README_RUS.md).
2. Check the [documentation index](docs/README.md), especially the
   [operations runbook](docs/OPERATIONS.md) and [API reference](docs/API.md).
3. Search existing issues for the exact error and environment.
4. Reproduce the problem from a clean checkout with locked dependencies.
5. Run the relevant verification commands and keep their non-secret output.

## Where to ask

| Request | Channel |
|---|---|
| Reproducible bug | Use the repository bug-report template |
| Feature proposal | Use the feature-request template |
| Dataset or model change | Use the ML/data change template |
| Usage question | Open a discussion if enabled; otherwise open a clearly labelled issue |
| Vulnerability or suspected secret exposure | Follow [`SECURITY.md`](SECURITY.md) privately |
| Conduct concern | Follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) privately |

Do not use a public issue for security details, credentials, access tokens,
private aerial media, identifiable people, farm coordinates, or RTSP addresses.

## Information to include

- the application revision or release;
- operating system, Python, `uv`, Node.js, and npm versions;
- execution mode: local SQLite, local PostgreSQL, or Docker Compose;
- the exact command and the smallest reproducible input using synthetic or
  shareable data;
- expected and actual behavior;
- sanitized logs and the `X-Request-ID`, when relevant;
- checks already performed;
- model version and checksum for inference behavior;
- whether the known dataset split leakage affects the claim being discussed.

Prefer text logs over screenshots so failures are searchable. Replace usernames,
absolute home paths, hostnames, database URLs, tokens, and media locations with
safe placeholders.

## What maintainers may close

Maintainers may close requests that cannot be reproduced, concern unsupported
private infrastructure, expose sensitive data, duplicate an existing issue, or
ask the current detector to make health, identity, legal-inventory, or other
unsupported claims. A closed request can be reconsidered when safe, reproducible
evidence is provided.

## Operational emergencies

This repository does not provide emergency monitoring. If a deployed instance
could affect animals, people, privacy, or farm operations, stop relying on its
output, isolate the affected component, preserve non-sensitive diagnostic
metadata, and use the operator's established incident process. The
[operations runbook](docs/OPERATIONS.md) contains containment and rollback
guidance.

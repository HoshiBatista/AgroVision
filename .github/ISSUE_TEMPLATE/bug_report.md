---
name: Bug report
about: Report a reproducible defect using safe, non-sensitive evidence
title: "[Bug] "
labels: bug
assignees: ""
---

## Summary

Describe the observable defect and its impact.

## Reproduction

1. Start from revision or release:
2. Run:
3. Provide this synthetic or shareable input:
4. Observe:

## Expected behavior

Describe the expected contract or user outcome.

## Environment

- Operating system:
- Python and `uv` versions:
- Node.js and npm versions, if relevant:
- Local SQLite, PostgreSQL, or Docker Compose:
- Model version and checksum, if relevant:
- Browser and version, if relevant:

## Verification and logs

List the checks already run and attach minimal sanitized text logs. Include the
`X-Request-ID` when available.

## Safety checklist

- [ ] I searched for an existing issue.
- [ ] I reproduced this from a clean checkout or described why I could not.
- [ ] I removed tokens, credentials, database URLs, private media, farm
      coordinates, personal data, and RTSP addresses.
- [ ] This is not a vulnerability. Security issues follow `SECURITY.md` privately.
- [ ] The input can be legally and safely shared.

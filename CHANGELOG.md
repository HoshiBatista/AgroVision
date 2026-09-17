# Changelog

All notable changes to AgroVision are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for
published releases. The repository currently represents a hackathon development
line; dates below mark project milestones rather than guaranteed production
support windows.

## [Unreleased]

### Added

- MIT license metadata for the Python and web projects.
- Central documentation index, architecture overview, contributor guide, code of
  conduct, governance and support policies, security policy, API reference,
  dataset card, model card, operations runbook, release checklist, roadmap, and
  issue templates.

### Changed

- Architecture decisions now use a consistent context, decision, consequences,
  limitations, and related-documents structure.
- Discovery material is explicitly marked as superseded by the selected
  AgroVision scope.
- Presentation guidance now includes reproducibility and preflight checks.

### Fixed

- PostgreSQL application-flow expectations now distinguish one confident
  detection from one uncertain detection.
- Local and Docker stream configurations use the tracked `misc/videos` paths.

## [0.1.0] - 2026-09-12

### Added

- YOLO26n aerial sheep detector with versioned metadata and SHA-256 verification.
- Image and video inference with confidence-aware counting and annotated outputs.
- File-backed drone streams, runtime RTSP connections, MJPEG tiles, and WebSocket
  dashboard updates.
- JWT authentication, Argon2 password hashing, roles, session journal, and CSV/PDF
  exports.
- FastAPI application, React and TypeScript web client, SQLite local mode, and
  PostgreSQL Docker mode.
- Reproducible data preparation, training, evaluation, and demo-generation entry
  points.
- Unit, contract, and PostgreSQL integration tests.
- Docker Compose deployment with non-root API and health checks.
- Bilingual English and Russian project READMEs with real screenshots and
  inference media.
- GitHub Actions workflow for Python quality, PostgreSQL tests, and frontend build.

### Known limitations

- Adjacent DJI video frames cross dataset splits, so baseline metrics are
  optimistic until a source-video or flight-grouped split is rebuilt.
- The system provides a visual estimate, not a certified inventory count or
  veterinary conclusion.

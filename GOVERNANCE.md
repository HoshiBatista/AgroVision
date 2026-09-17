# Governance

AgroVision uses lightweight maintainer governance suited to a focused hackathon
product. Decisions should remain traceable to user value, reproducible evidence,
and the engineering agreement in [`AGENTS.md`](AGENTS.md).

## Roles

### Contributors

Anyone who reports a reproducible issue, improves documentation, reviews a
change, contributes code, or strengthens data/model evidence is a contributor.
Contributors follow the [code of conduct](CODE_OF_CONDUCT.md), contribution
guide, licenses, and data-handling rules.

### Reviewers

Reviewers evaluate changes in areas they understand. They check behavior,
architecture boundaries, tests, security, documentation, and the validity of ML
claims. Review does not transfer responsibility away from the author or
maintainer.

### Maintainers

Maintainers are repository owners with permission to triage issues, approve and
merge changes, manage releases, moderate project spaces, and respond to private
reports. Repository access controls are the source of truth for current
maintainer status; this document does not invent a permanent name list.

## Decision process

Routine changes use pull-request review and automated checks. A maintainer may
merge when the scope is clear, required evidence passes, review comments are
resolved, and documentation reflects the resulting behavior.

Material decisions require a short architecture decision record before or with
implementation. This includes:

- changing product scope or the primary user workflow;
- selecting a new dataset, model architecture, or second model;
- changing an API compatibility promise or persistence technology;
- adding a distributed component, hosted inference dependency, or paid service;
- weakening model integrity, privacy, security, or reproducibility controls.

ADRs record context, alternatives, decision, consequences, limitations, and
follow-up. Accepted ADRs remain as history; superseding decisions add a new ADR
and link both records.

## Evidence and approval

Approval depends on the kind of change:

| Change | Required evidence |
|---|---|
| Documentation only | Valid links, factual consistency, and review |
| Domain/application behavior | Focused tests plus repository quality gates |
| API or web behavior | Contract tests and relevant frontend verification |
| Persistence or migration | PostgreSQL integration test and rollback analysis |
| Dataset | Provenance, license, immutable version, audit, and grouped-split analysis |
| Model | Reproducible configuration, independent evaluation, latency, checksum, and model card |
| Release/deployment | Release checklist, migration review, security review, and rollback evidence |

Passing automation is necessary but not sufficient for model or product claims.
A maintainer can request field evidence, threat review, or an operational drill
when the risk warrants it.

## Conflicts and recusal

People should disclose a material conflict of interest and avoid being the sole
approver of their own high-risk change. A maintainer who is the subject of a
conduct or security report must not control that report's investigation. When
maintainers disagree, prefer a small reversible experiment and record the result;
otherwise preserve the current accepted decision until stronger evidence exists.

## Security and conduct decisions

Security reports follow [`SECURITY.md`](SECURITY.md) and may be handled privately
until coordinated disclosure. Conduct reports follow
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Confidential information is shared
only with people necessary to assess and resolve the issue.

## Releases and reversibility

Releases bind an application revision, dependency lock, database migrations,
configuration, model version, and model checksum. Maintainers must be able to
identify the previous known-good release and its compatible data state. Use the
[release checklist](docs/RELEASE_CHECKLIST.md) and
[operations runbook](docs/OPERATIONS.md); do not declare production readiness
from CI alone.

## Changing governance

Governance changes use a pull request, explicit review, and a changelog entry.
They must not silently weaken the code of conduct, private security reporting,
license obligations, or the requirement to report model limitations.

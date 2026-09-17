# AgroVision documentation

This directory contains the decisions, evidence, and presentation material that
support the product claims in the main [English](../README.md) and
[Russian](../README_RUS.md) documentation.

## Start here

| Document | Purpose | Status |
|---|---|---|
| [ADR 0001](adr/0001-aerial-sheep-baseline.md) | Dataset, training baseline, and evaluation caveat | Accepted |
| [ADR 0002](adr/0002-product-scope.md) | Product scope, user, workflow, and stack deviations | Accepted |
| [ADR 0003](adr/0003-model-runtime-and-containers.md) | Model integrity, inference serialization, and deployment | Accepted |
| [Presentation guide](presentation/README.md) | Pitch deck assets, regeneration, and safety rules | Current |
| [Speaker notes](presentation/speaker_notes.md) | Seven-to-nine-minute defense and live-demo script | Current |
| [Project ideas](PROJECT_IDEAS.md) | Archived topic discovery that preceded AgroVision | Superseded |

## Documentation principles

- Product claims must point to measured results or versioned configuration.
- Dataset leakage and model limitations must appear next to reported metrics.
- ADRs preserve the reason for a decision, not only its final implementation.
- Generated artifacts are reproducible from repository commands and remain out
  of Git unless they are deliberate presentation assets.
- Secrets, raw datasets, model weights, uploads, and private RTSP addresses are
  never embedded in documentation.

## Source of truth

The precedence for project decisions is:

1. [`AGENTS.md`](../AGENTS.md) for the engineering working agreement;
2. accepted ADRs for scoped architectural and product decisions;
3. versioned configuration for concrete runtime and model values;
4. README files for onboarding and operation;
5. archived discovery documents for historical context only.

If documentation and executable configuration disagree, treat that as a defect
and update the affected document or record a new ADR.

## License

Original project code and documentation are available under the
[MIT License](../LICENSE). Third-party datasets, dependencies, pretrained
checkpoints, and media retain their own licenses and usage terms.

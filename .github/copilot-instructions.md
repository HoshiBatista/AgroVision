# GitHub Copilot repository instructions

Follow `/AGENTS.md` as the canonical project instructions. Respect its modular
architecture, inward dependency direction, typed boundaries, reproducible ML
workflow, secret handling, and definition of done.

The selected topic and one-model MVP are recorded in
`/docs/adr/0002-product-scope.md`. Treat `/docs/PROJECT_IDEAS.md` as superseded
discovery context.

Generate Python 3.12 code with explicit types and small cohesive functions. Keep
framework code out of the domain layer. Never place secrets, local paths, dataset
archives, model weights, or generated artifacts in source control.

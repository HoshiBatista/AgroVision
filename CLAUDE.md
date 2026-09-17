# Claude instructions

Read and follow [`AGENTS.md`](AGENTS.md) in full before making changes. It is the
canonical source for the working agreement, architecture, ML reproducibility,
security, verification, and definition of done.

The selected product is AgroVision. Use the accepted architecture decisions as
the source of truth:

- [`ADR 0001`](docs/adr/0001-aerial-sheep-baseline.md) for the dataset and model
  baseline;
- [`ADR 0002`](docs/adr/0002-product-scope.md) for product scope;
- [`ADR 0003`](docs/adr/0003-model-runtime-and-containers.md) for inference and
  deployment decisions.

[`docs/PROJECT_IDEAS.md`](docs/PROJECT_IDEAS.md) is superseded discovery context,
not active product direction. Do not duplicate or weaken `AGENTS.md` here. If
instructions conflict, follow the user's current request, then `AGENTS.md`, then
this file.

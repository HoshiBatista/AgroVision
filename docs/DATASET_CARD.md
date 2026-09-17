# Dataset card: Aerial Sheep v1

This card records the provenance, preparation, known defects, and intended use
of the dataset behind the AgroVision baseline. It must be read with
[ADR 0001](adr/0001-aerial-sheep-baseline.md); the recorded metrics are not
independent flight-level estimates.

## Identity and provenance

| Field | Value |
|---|---|
| Provider | Roboflow Universe |
| Owner/workspace | `riis` |
| Dataset | `aerial-sheep` |
| Version | 1 |
| Source | [Roboflow Universe dataset page](https://universe.roboflow.com/riis/aerial-sheep/dataset/1) |
| Task | Object detection |
| Classes | 1 (`sheep`) |
| Published license | Public Domain |
| Provider export timestamp | 2024-10-10 09:37 GMT |
| Project acquisition and audit date | 2026-09-12 |
| Raw local root | `data/raw/aerial-sheep-1` |
| Processed local root | `data/processed/aerial-sheep-1-yolo` |

The provider's page is the authority for upstream attribution and license
status. Reconfirm its terms before redistributing the raw export. The dataset is
not committed to this repository.

## Composition

Preparation retains all images and removes only invalid zero-area boxes from the
generated training view.

| Split | Images | Valid objects after cleaning | Removed boxes |
|---|---:|---:|---:|
| Train | 3,609 | 113,494 | 48 |
| Validation | 350 | 11,334 | 3 |
| Test | 174 | 5,603 | 0 |
| Total | 4,133 | 130,431 | 51 |

The provider export uses 600 x 600 stretch resizing, auto-orientation, and
generated augmented variants. Those transformations are part of the received
version and should be considered when comparing it with a future raw-source
dataset.

## Intended use

The dataset supports a technical baseline for detecting and visually counting
sheep in aerial imagery. It is appropriate for pipeline development, local demo
validation, and controlled comparisons in this repository.

It does not establish accuracy for:

- a new farm, landscape, season, breed, camera, altitude, or flight pattern;
- animal identity, health, weight, sex, welfare, or ownership;
- legal inventory, billing, insurance, or autonomous animal-management actions;
- ground-level, thermal, satellite, or non-aerial imagery.

## Preparation and reproducibility

Keep the raw export immutable. The preparation command creates relative image
links, cleaned labels, a generated `data.yaml`, and
`preparation_report.json` in the processed directory:

```bash
make prepare
```

Configuration is versioned in
[`configs/train_yolo26n_aerial_sheep.toml`](../configs/train_yolo26n_aerial_sheep.toml),
and implementation lives in
[`ml/data/prepare_aerial_sheep.py`](../ml/data/prepare_aerial_sheep.py). A clean
run should reproduce the table above. A different count is a provenance or
preparation failure and must be investigated before training.

Raw data, processed data, download caches, and generated predictions remain out
of Git. Do not overwrite the user's provider export to repair annotations.

## Annotation audit

The project checks split structure, readable images, label syntax, class IDs,
normalized box bounds, positive box area, object counts, exact identities, and
near-duplicate visual content. The processed view excludes 51 zero-area boxes
while preserving the source files for auditability.

Qualitative review is still required. Dense flocks and very small objects make
exhaustive annotation difficult, and missing or ambiguous sheep can directly
affect both detector metrics and counting error.

## Known split leakage

The supplied train, validation, and test folders are not independent by source
video or flight. Adjacent frames from at least seven DJI videos cross splits.
The audit also found 221 cross-split image pairs with a 64-bit difference-hash
distance of two or less. Exact duplicates and exact source IDs do not cross
splits, but neighboring frames remain visually very similar.

This leakage can make precision, recall, mAP, and counting results optimistic.
Every baseline metric must be presented with this warning. The current test set
must not be described as an independent field test.

## Bias, privacy, and representativeness

Coverage is limited to the conditions present in the provider export. The card
does not claim balanced representation across geography, breeds, terrain,
weather, flock density, capture height, camera hardware, or image quality.

Although the target is livestock, aerial data may incidentally contain people,
vehicles, property, or location clues. Operators are responsible for lawful
collection, access control, retention, and redaction for any additional field
data. Do not upload private imagery to external services as part of the default
workflow.

## Required next dataset version

A product-quality evaluation requires a new version with:

1. stable source-video, flight, farm, or capture-session identifiers;
2. grouped train, validation, and test splits with no adjacent-frame leakage;
3. a documented annotation review and representative-sample gallery;
4. threshold selection on validation data only;
5. one final held-out evaluation plus comparison with manual field counts.

The new dataset must receive its own versioned manifest and must not silently
replace version 1. See the [roadmap](ROADMAP.md) and
[model card](MODEL_CARD.md) for the corresponding release gate.

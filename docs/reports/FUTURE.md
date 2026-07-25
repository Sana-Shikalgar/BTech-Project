# Future Work

This file documents planned refactors and other future work. Nothing described here has been
done yet — it's a plan for later, not a changelog.

## Planned: extract duplicated notebook logic into shared `src/` modules

**Status: not started.** `dataset_config.py` exists today and is used by all 13 migrated
notebooks, but it only resolves paths (`RAW_DIR`, `FINAL_DIR`) — no actual data-loading or
model-architecture code has been extracted into an importable module yet. The notebooks remain
the source of truth for how data is loaded and how the models are built. This section documents
the plan for when someone does that extraction.

### Goal

Pull the logic currently duplicated (near-verbatim, copy-pasted) across notebooks into shared,
importable `.py` modules under `src/`, so notebooks become thin orchestration layers — call into
`src/`, run training/inference, inspect results — instead of each one containing a full,
independently-maintained copy of the same dataset-loading and model-definition code.

### Proposed structure

```
src/
  data.py         (dataset loading: transform pipeline + datasets.ImageFolder(...)
                   instantiation, parameterized by RAW_DIR/FINAL_DIR subfolder name)
  models/
    cnn.py           (customized CNN architecture)
    efficientnet.py  (EfficientNetB0 fine-tuning wrapper)
    hybrid.py        (CNN + EfficientNetB0 fusion architecture)
  training.py      (shared training loop: AdamW, cosine annealing, early stopping, label
                     smoothing — the recipe documented in experiments/TUNING_NOTES.md)
```

### `data.py` — actual duplication findings (verified by scanning all 13 notebooks, not assumed)

**Correction to the structure sketch above:** only 10 of the 13 migrated notebooks actually use
`datasets.ImageFolder` + `transforms.Compose` — the 3 `dataset_pipeline/` notebooks
(`dataset_analysis.ipynb`, `dataset_balancing.ipynb`, `dataset_balance_visualization.ipynb`) do
**not**. They operate on raw folders directly via `os.walk`/`os.listdir` (and, for
`dataset_balancing.ipynb`, TensorFlow's `ImageDataGenerator` for augmentation) and only share the
`RAW_DIR`/`FINAL_DIR` path-resolution bootstrap with the other 10 — not any dataset-loading logic
in the `ImageFolder` sense. A `data.py` module extracted from the `ImageFolder` pattern would not
apply to these 3 notebooks as-is.

The other 10 (6 model notebooks, 2 demo notebooks, `experiments/02_*`, `experiments/03_*`):

- **Identical everywhere:** the transform pipeline —
  `transforms.Compose([transforms.Resize(255), transforms.CenterCrop(224), transforms.ToTensor()])`
  — is byte-for-byte identical across all 10. `num_workers=2` and `pin_memory=True` are likewise
  identical in every notebook that builds a `DataLoader`.
- **Varies — which dataset:** the `FINAL_DIR` subfolder passed to `ImageFolder` (
  `plantvillage_balanced` vs `new_plant_diseases_balanced`), obviously dependent on which dataset
  the notebook targets.
- **Varies — batch size:** 9 of the 10 use `batch_size = 16`; `experiments/02_stratified_split_50_epoch_breakthrough.ipynb`
  uses `batch_size = 32`. This is a genuine, deliberate divergence (it's an experiment notebook)
  and a real parameter a shared module would need to expose, not hardcode.
- **Varies — whether a `DataLoader`/batch size exists at all:** the 2 `demo/` notebooks only
  instantiate the `ImageFolder` dataset (for single-image inference) and never build a
  `DataLoader` or set `batch_size` — unlike the 8 training/experiment notebooks.

So a shared `data.py` should parameterize: dataset name/subfolder, batch size, and whether a
`DataLoader` is needed — not just copy one notebook's version verbatim.

### `models/` — actual duplication findings (verified by scanning all 6 model notebooks)

- **CNN:** `models/plantvillage/cnn/cnn.ipynb` and `models/new_plant_diseases/cnn/cnn.ipynb`
  define an identical `class CNN(nn.Module)` (same `conv_layers`/`dense_layers` structure,
  same layer sizes) — the only difference is the `K` (class count) constructor argument, which
  is already a parameter, not hardcoded. Directly extractable as-is.
- **EfficientNet:** `models/plantvillage/efficientnet/efficientnet.ipynb` and
  `models/new_plant_diseases/efficientnet/efficientnet.ipynb` define an identical
  `class EfficientNetB0_Model(nn.Module)` (loads `efficientnet_b0` with ImageNet weights,
  replaces the final classifier layer with `nn.Linear(in_features, K)`). Directly extractable.
- **Hybrid:** both `hybrid.ipynb` notebooks define `class CNNFeatureExtractor(nn.Module)` and
  `class HybridModelEfficientNet(nn.Module)`. `CNNFeatureExtractor`'s own in-notebook comment
  states it reuses "the same conv layers as your CNN" — i.e. the same `conv_layers` block as
  the standalone `CNN` class, minus `dense_layers`, fused with an EfficientNet-B0 branch
  (1024 + 1280 → 1024 → K). This means the CNN conv-layer block is actually duplicated in
  **three** places, not two: both `cnn.ipynb` files and both `hybrid.ipynb` files' feature
  extractor — a `models/cnn.py` extraction should factor out that shared conv block so
  `hybrid.py` can reuse it directly rather than re-copying it a third and fourth time.

### Scope note

This is a plan only. `dataset_config.py` (path resolution) is the only piece of this that
currently exists as a shared module. No `src/` directory, no `data.py`, no `models/*.py`, no
`training.py` exist yet — until this refactor happens, every notebook listed above remains the
authoritative, independently-runnable copy of its own logic.

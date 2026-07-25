# Tuning journey: Customized CNN

This traces how the Customized CNN's training recipe evolved from the first working
prototype to the final configuration now in `models/plantvillage/cnn/` and
`models/new_plant_diseases/cnn/`. All numbers below were pulled directly from each
notebook's own printed training output and/or its paired `metrics_*.xlsx` classification
report (validation/test sheets, not the train sheet). Four representative milestones from
this journey are copied into this folder; every other variant mentioned is still in its
original location and untouched.

## Phase 0 — earliest prototype (root-level `plant-disease-detection-plant_village.ipynb`)

Before any of the phases below, there was a standalone Google Colab notebook
(`plant-disease-detection-plant_village.ipynb`, → `experiments/00_early_prototype_colab.ipynb`)
— PlantVillage only, mounting a dataset zip from Google Drive. It uses the same basic
4-conv-block CNN architecture, trained for just **5 epochs** with plain `Adam` (no LR
scheduler, no stratified split — just a shuffled `SubsetRandomSampler`). Results: **Train
96.7% / Test 98.9% / Validation 98.7%**. These numbers are notably higher than the "first
working baseline" in Phase 1 below despite near-identical settings (also 5 epochs, plain
Adam) — likely just a favorable run and/or a different underlying data split, illustrating
the same run-to-run instability discussed in Phase 1. This notebook also predates the
project's later two-dataset scope decision and its own single-image inference loop (using
`disease_info.csv`) is the ancestor of the pattern later reused in `demo/`.

## Phase 1 — first working baseline (`Trail 1/Jupyter Dataset 02/`, Jan-Feb 2025)

The team's first CNN was the 4-conv-block architecture that's still in use today (two
`Conv2d+ReLU+BatchNorm` per block, dropout 0.4, a 1024-unit dense layer). Trained with
plain `Adam` (default params), no LR scheduler, 5 fixed epochs, on an early, smaller
version of PlantVillage (~61,500 images before the later re-balancing work).

- **`D02-Original.ipynb`** (→ `experiments/01_baseline_first_working_cnn.ipynb`): the first
  working baseline. Train 87.13% / Test 84.24% / Val 83.75%.
  **Note on its dataset path:** unlike every other notebook in this folder,
  `01_baseline_first_working_cnn.ipynb` was intentionally left unmodified and still points at
  its original hardcoded path (`../All_Datasets/Plant_leaf_diseases_dataset_with_augmentation/...`)
  rather than the shared `dataset_config.py`/`DATA_ROOT` convention the other notebooks now use.
  That path's depth doesn't cleanly match either its original folder (`Trail 1/Jupyter Dataset 02/`,
  two levels deep) or its current one (`experiments/`, one level deep) in an obviously-correct way —
  it may never have resolved correctly outside whatever working directory the original author's
  Jupyter session happened to be launched from. Treat this notebook's dataset path as
  **historical/unverified**, not something to run as-is.
- A same-config rerun (`D02-Original-Copy1.ipynb`) landed at Test 80.98% / Val 79.02% —
  a ~3-5pp swing from the exact same settings, an early sign of the run-to-run instability
  the project's summary doc later describes as "fluctuating results."
- Ablations tried at this stage, each changing exactly one thing from the baseline:
  - Dropout 0.4 → 0.5 (`D02-Dropout-inc.ipynb`): Test dropped to 78.84% — *worse*, not better.
  - Epochs 5 → 20 (`D02-Original-epoch-inc.ipynb`): Test jumped to 96.13% — by far the
    single biggest lever found in this phase.
  - Dropout 0.5 + epochs 20 together (`D02-Dropout-inc-epoch-inc.ipynb`): Test 96.06%,
    no better than epochs alone — confirms dropout wasn't the fix.
  - Adam with explicit `lr=0.001, weight_decay=1e-4` (`D02-change-in-adam-optimizer.ipynb`):
    Test 86.14%, a modest gain, still at 5 epochs.
- Side branches abandoned here: **PlantDoc** (`Jupyter Dataset 04`) was explored and
  dropped — after reading more on the classification-vs-detection distinction, the team
  judged it out of scope, and results were poor anyway (Test accuracy near 0-10%). An
  early **New Plant Diseases** attempt (`Jupyter Dataset 05`) got a reasonable ~80% Test,
  but its "-balanced" variant collapsed to near-random accuracy (~2%) — read as a broken
  run rather than real evidence about balancing, since it isn't corroborated anywhere else.
- **Takeaway carried forward:** epoch count mattered far more than dropout at this stage;
  the instability itself wasn't solved yet.

## Phase 2 — sampling strategy and the 50-epoch breakthrough (`New Trails/`, Feb 20 - Mar 10)

Work now settled on the two final datasets, rebalanced "category-wise" (2,000 images per
disease class, not per plant species — see below), and shifted focus to *how the data was
split* and *how long/how carefully training ran*.

- **Feb 20:** Plain, non-stratified hold-on split, 5 epochs, plain Adam
  (`D02-Category.ipynb`): Val 92.38% / Test 92.00%. In parallel, a "plant-wise" balanced
  dataset was tried (`Rejected Ideas/D02-Plant.ipynb`) — overall accuracy looked fine
  (Val 93.39%) but macro-averaged metrics were much worse (macro F1 ~0.85 vs weighted
  ~0.93), because balancing by plant species doesn't guarantee balance across the actual
  disease-category classes being predicted. **Rejected** in favor of category-wise
  balancing, which every later notebook uses.
- **Feb 21-22:** Switched to a stratified 80/10/10 hold-on split
  (`D02-Category-stratified-hold-on.ipynb`): Val 92.17% / Test 92.08% — about the same as
  plain hold-on *at this point*, since nothing else had changed yet, but it removed a
  source of split-to-split variance going forward.
- **Feb 25:** Two branches off the stratified baseline, both filed under `Rejected Ideas/`:
  - 5-fold stratified cross-validation (`D02-Category-Cross-Fold.ipynb`): mean Test
    accuracy ~89.96% across folds (worse than hold-on) with high per-class variance
    across folds, at roughly 5x the compute cost. **Rejected** — not worth it for this
    dataset size.
  - A longer stratified run with `AdamW` + `ReduceLROnPlateau` +
    `EarlyStopping(patience=5)`, no label smoothing yet, early-stopped at epoch 16
    (`D02-Category-hold-on-Copy2.ipynb`): Val 94.91% / Test 95.27% — a decent result with
    no explicit rejection reason recorded; most likely just superseded by the next step.
- **Feb 26-27:** Added `weight_decay=1e-4` and `label_smoothing=0.1` on top of the
  stratified split + AdamW + ReduceLROnPlateau + early stopping recipe. At a **fixed
  5 epochs** (`...-schedular-early-stop-epoch-5.ipynb`) this gave no benefit yet
  (Val 91.78% / Test 92.35%). Letting it run **up to 50 epochs**, early-stopping at
  epoch 38 (`D02-inc-epoch-to-50.ipynb`, → `experiments/02_stratified_split_50_epoch_breakthrough.ipynb`):
  **Val 98.94% / Test 98.79%** — the single largest jump anywhere in the project (from
  ~92% to ~99%). This recipe — stratified split, AdamW, weight decay, label smoothing,
  ReduceLROnPlateau, early stopping, up to 50 epochs — became the template later applied
  to every model (CNN, EfficientNetB0, Hybrid) on both datasets.
- **Mar 6-10:** The same recipe was re-run per final model/dataset combination inside
  `New Trails/PlantVillage/` and `New Trails/NewPlantDisease/` (e.g. Val 97.50% / Test
  97.51% for the PlantVillage CNN re-run) — close to, but not identical to, the Feb 27
  numbers, consistent with normal run-to-run variance.

## Phase 3 — scheduler and learning-rate tuning (`Customized CNN/`, Mar 14-18)

With the New Trails recipe as a starting point (re-baselined here as
`Plant Village - plateau-delta001-lr001/`: Val 96.76% / Test 97.09%), the team tuned the
two knobs the project summary specifically calls out: the LR scheduler and the learning
rate / early-stop delta pairing.

- **Scheduler swap, same LR (0.001):** Replacing `ReduceLROnPlateau` with
  `CosineAnnealingLR` in isolation (`PlantVillage/cosine schedular/`) actually scored
  slightly *lower* — Val 96.23% / Test 96.49% — than the plateau baseline. Cosine
  annealing's benefit (a smoother loss curve, per the project summary) didn't show up as
  a raw accuracy win until combined with a lower learning rate (see final config below).
- **Tighter early-stop delta (0.001 → 0.0005), still on plateau**
  (`PlantVillage/reduce delta/`): let training run longer (35 vs 22 epochs) and improved
  to Val 97.90% / Test 98.04%.
- **Lower learning rate (0.001 → 0.0001), still on plateau, delta back to 0.001**
  (`PlantVillage/reduce lr/`, → `experiments/03_reduce_lr_before_cosine_annealing.ipynb`):
  **Val 99.14% / Test 99.15%**, early-stopping at epoch 37 — the single biggest jump in
  this phase, and in fact the **highest CNN+PlantVillage accuracy found anywhere in the
  project**, including the eventual final config.
- **Final config** (`PlantVillage/ultimate (cosine-delta0001-lr0001)/`, now in
  `models/plantvillage/cnn/`): combines Cosine Annealing + lr=0.0001 + delta=0.0001 →
  **Val 98.5% / Test 98.24%** — a touch below the isolated "reduce lr" plateau run above.
  The team's own notes explain the choice wasn't purely about squeezing out the last
  fraction of a percent on this one dataset: cosine annealing gave a smoother, more
  stable loss curve, and — importantly — this exact combined recipe (lr=0.0001,
  delta=0.0001, Cosine Annealing, batch size 16) was the one that was **successfully and
  uniformly applied across all three architectures (CNN, EfficientNetB0, Hybrid) on both
  datasets**, which the standalone "reduce lr" plateau variant above was never tested
  against. Consistency across the full comparative study won out over a fractional
  single-model peak.

## A data-quality caveat worth flagging

The New Plant Diseases equivalents of the "cosine scheduler" and "reduce delta" ablation
notebooks under `Customized CNN/NewPlantDisease/` were found to contain **stale, copied
outputs from the PlantVillage runs** — their displayed metrics and even per-epoch timing
match the PlantVillage notebooks byte-for-byte, despite the code pointing at the New
Plant Diseases data. The "reduce lr" New Plant Diseases notebook is similarly incomplete
(only one stale epoch of output). In other words: the phase-3 "which knob mattered most"
story above is solidly evidenced for **PlantVillage**, but the equivalent intermediate
data points for **New Plant Diseases** don't actually exist in this repo — only its
plateau baseline (Val 97.99% / Test 98.13%) and final config numbers are trustworthy.

## Where the final models live

The production configuration from Phase 3 — Cosine Annealing, lr=0.0001, early-stop
delta=0.0001, batch size 16, AdamW, weight decay 1e-4, label smoothing 0.1, stratified
80/10/10 split — is what's packaged in **`models/plantvillage/cnn/`** and
**`models/new_plant_diseases/cnn/`**.

# Crop Disease Classification with CNN, EfficientNetB0, and a Hybrid Model

Comparing a customized CNN, a fine-tuned EfficientNetB0, and a CNN+EfficientNetB0 hybrid
architecture for plant leaf disease classification.

## Overview

This project benchmarks three deep learning architectures (a from-scratch CNN, a
transfer-learned EfficientNetB0, and a hybrid model that fuses both) against each other on
two public plant disease datasets (PlantVillage and New Plant Diseases). The core question
isn't just "which model scores highest," but how each one handles class imbalance in the raw
data: both datasets are rebalanced to a fixed image count per class before training, and the
project tracks how that rebalancing step (plus the training recipe layered on top of it:
sampling strategy, LR scheduling, batch size) affects generalization on held-out test data.
The full experimentation history, including the dead ends and not just what shipped, is kept
in `experiments/`, since a large part of the actual work was in that tuning process rather
than the final numbers alone.

## Tech Stack

Pulled directly from `environment.yml`:

- **Python 3.8**
- **PyTorch >= 2.0** and **torchvision >= 0.15** (model architectures, training, inference)
- **TensorFlow >= 2.10** (`ImageDataGenerator`, used only in the dataset-balancing/augmentation
  step, not for any model)
- **scikit-learn >= 1.0** (stratified splitting, classification reports)
- **NumPy >= 1.21**, **pandas >= 1.3**, **Matplotlib >= 3.5**, **Seaborn >= 0.11**,
  **Pillow >= 9.0**
- **tabulate >= 0.9** (per-class accuracy tables), **tqdm >= 4.60**,
  **albumentations >= 1.3**
- **openpyxl >= 3.0** (reading/writing the `metrics.xlsx` classification reports)
- **JupyterLab >= 3.0** / **notebook >= 6.4** / **nbformat >= 5.0**
- **torchsummary** (via pip, not available on conda-forge)

Install with `conda env create -f environment.yml` (env name: `crop-disease-classification`).

## Results

Test-set metrics, read directly from each model's `metrics.xlsx` (`weighted avg` row for
Precision/Recall/F1) and cross-checked against `docs/reports/Report.pdf` Tables 6.1-6.6:

| Model | Dataset | Accuracy | Precision | Recall | F1-score |
|---|---|---|---|---|---|
| Customized CNN | PlantVillage | 98.24% | 98.25% | 98.24% | 98.23% |
| Customized CNN | New Plant Diseases | 99.16% | 99.18% | 99.16% | 99.16% |
| EfficientNetB0 | PlantVillage | 99.79% | 99.80% | 99.79% | 99.79% |
| EfficientNetB0 | New Plant Diseases | 99.89% | 99.89% | 99.89% | 99.89% |
| Hybrid (CNN + EfficientNetB0) | PlantVillage | 99.82% | 99.82% | 99.82% | 99.82% |
| Hybrid (CNN + EfficientNetB0) | New Plant Diseases | 99.87% | 99.87% | 99.87% | 99.87% |

EfficientNetB0 and the Hybrid model both comfortably beat the from-scratch CNN on both
datasets, with the Hybrid model edging out plain EfficientNetB0 on PlantVillage and roughly
tying it on New Plant Diseases: transfer learning from ImageNet clearly helps more than the
extra architectural complexity of fusing in the custom CNN branch does. Worth noting: the
shipped CNN config (Cosine Annealing + lr=0.0001 + delta=0.0001) is *not* the single
highest-scoring CNN variant found during tuning: an isolated PlantVillage run using
`ReduceLROnPlateau` instead scored slightly higher (Test 99.15%, see
`experiments/TUNING_NOTES.md`). The shipped config was chosen because it was the one recipe
validated consistently across all three architectures and both datasets, not because it was
the single best score on one dataset.

## Repo Structure

```
models/             Final model artifacts: 3 architectures x 2 datasets, each with its
                     training notebook, saved weights (weights.pt), and metrics.xlsx
demo/                Standalone single-image inference notebooks for each dataset,
                     plus disease_info.csv (used to display disease details for a prediction)
dataset_pipeline/    Dataset analysis, class-balance visualization, and the balancing
                     notebook that turns raw downloaded data into the final training sets
experiments/         The tuning journey: 4 milestone notebooks (earliest prototype through
                     the final recipe) plus TUNING_NOTES.md, which documents what was tried,
                     what worked, what didn't, and why
docs/                docs/reports/ (project report, data setup guide, tuning summary, future
                     work plan) and docs/figures/ (loss curves, confusion matrices, per-class
                     accuracy charts referenced by the report)
dataset_config.py    Single source of truth for dataset paths (RAW_DIR, FINAL_DIR under
                     data/); every notebook imports from here instead of hardcoding paths
environment.yml      Conda environment definition (see Tech Stack above)
check_data_setup.py  Verifies data/ is laid out correctly (folder structure, class names,
                     rough image counts) before you try running any notebook
```

## Running This Project

If you're setting this up from a fresh clone/fork:

1. **Clone the repo and create the environment:**
   ```
   git clone <this-repo-url>
   cd BTech-Project
   conda env create -f environment.yml
   conda activate crop-disease-classification
   ```
2. **Get the data.** This repo doesn't include the datasets (too large for git). Briefly:
   PlantVillage and New Plant Diseases both come from Kaggle. Full download links, exact
   folder layout, and the balancing step are documented in
   [`docs/reports/DATA_SETUP.md`](docs/reports/DATA_SETUP.md), follow that end to end before
   running anything else.
3. **Verify the data layout:**
   ```
   python check_data_setup.py
   ```
   This checks folder structure, class names, and rough image counts, and will catch a wrong
   download or missed step before you waste time running a notebook against bad data.
4. **Explore in this order:** `dataset_pipeline/` (how the raw data was analyzed and
   balanced), then `models/` (training and evaluation per architecture/dataset), then
   `demo/` (single-image inference using the trained weights).
5. **For full methodology, literature review, and detailed per-category results**, this
   repo doesn't repeat them in prose: see [`docs/reports/Report.pdf`](docs/reports/Report.pdf).

## The Tuning Journey

`experiments/TUNING_NOTES.md` traces the CNN's training recipe from the first working
prototype (5 epochs, plain Adam, Test ~84%) through several rounds of ablation to the final
shipped config. The single biggest jump in the entire project came from one change: moving
to a stratified train/val/test split and letting training run up to 50 epochs (with early
stopping), which took validation accuracy from roughly **92% to roughly 99%** in one step,
far more impactful than any of the scheduler, learning-rate, or dropout tweaks tried before
or after it. That document is also honest about the config actually shipped not being the
single best-scoring variant found (see Results above); it was chosen for being the recipe
that generalized consistently across all three architectures, not for winning on one dataset
in isolation.

## Authorship

This was a 3-person academic team project. I built the dataset pipeline (analysis, balancing,
class-imbalance handling), all three model architectures (Customized CNN, EfficientNetB0,
Hybrid), and the training, tuning, and evaluation work documented in experiments/ and models/.
My teammates handled the written report and UI-related work.

## A Note on This Repo's History

This project was originally developed locally over several months without git: training
notebooks, dataset experiments, and results accumulated as local folders and file copies
rather than commits. The repository was reorganized and published after the project was
already complete: scattered notebooks were traced back to the results in the report, curated
into the structure you see now, and the dataset paths were migrated to the shared
`dataset_config.py` convention. `experiments/TUNING_NOTES.md` reconstructs the tuning
timeline from each notebook's own saved output rather than from commit history, since none
exists for that period.

## Limitations

All models were evaluated on curated benchmark datasets (PlantVillage and New Plant
Diseases), not on images collected in real-world field conditions. Real-world deployment
would need validation against field-captured images (different lighting, backgrounds, camera
quality, and disease co-occurrence than these lab-style datasets) before the reported
accuracy figures could be expected to hold.

## License & Acknowledgments

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**; see
[`LICENSE`](LICENSE) for the full text.

Thanks to project supervisor **Dr. Sunil B. Mane**, COEP Technological University, Pune, for
guidance throughout the project.

## Full Report

For complete methodology, literature review, and detailed results (including per-category
breakdowns and confusion matrices for all six model/dataset combinations), see
[`docs/reports/Report.pdf`](docs/reports/Report.pdf).

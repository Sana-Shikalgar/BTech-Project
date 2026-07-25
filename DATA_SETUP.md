# Data Setup

This repository does not include the image datasets (too large for GitHub, and both are
publicly available). This document explains how to download and arrange them so that the
notebooks in `dataset_pipeline/`, `models/`, `demo/`, and `experiments/` run as-is.

## 1. Expected folder structure

Create a `data/` folder at the project root with this layout:

```
data/ 
  raw/
    plantvillage_raw/
    new_plant_diseases_raw/
    plantdoc_raw/                     (optional — not used by any final model, kept for provenance only)
  final/
    plantvillage_balanced/
    plantvillage_balanced_by_plant/   (a rejected alternative balancing approach — see
                                       experiments/TUNING_NOTES.md; not used by any shipped model)
    new_plant_diseases_balanced/
```

`data/` is git-ignored — nothing under it is (or should be) committed.

## 2. Download the raw datasets

### PlantVillage (raw)
Source: **Kaggle — `sravanneeli/plant-leaf-diseases-dataset-with-augmentation`**
https://www.kaggle.com/datasets/sravanneeli/plant-leaf-diseases-dataset-with-augmentation

(Original source: Mendeley Data, "Identification of Plant Leaf Diseases Using a 9-layer Deep
Convolutional Neural Network," https://data.mendeley.com/datasets/tywbtsjrjv/1 — 39 classes,
61,486 images, six augmentation techniques already applied. This is **not** the same as the
plain `emmarex/plantdisease` PlantVillage mirror — that one is a different, smaller,
non-augmented dataset and will not reproduce the same results.)

Download and extract so that the 39 class folders (e.g. `Apple___Apple_scab`,
`Tomato___healthy`, etc.) sit directly inside `data/raw/plantvillage_raw/`.

### New Plant Diseases (raw)
Source: **Kaggle — `vipoooool/new-plant-diseases-dataset`**
https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset

This dataset ships as separate `train/` and `valid/` splits. The pipeline used in this project
expects a single flat folder of 38 class subfolders (matching the report's stated 87,900
original images). **You will likely need to merge `train/` and `valid/` into one folder per
class before running the balancing notebook** — `dataset_pipeline/dataset_balancing.ipynb`
contains a combine step for this; check its "Combining the train and valid folders" section
before running the main balancing step, and verify the resulting flat folder's class counts
against `check_data_setup.py` (see below) before proceeding. Place the resulting flat structure
at `data/raw/new_plant_diseases_raw/`.

### PlantDoc (raw, optional)
Not required to reproduce any of the shipped models — the project's own investigation found
PlantDoc was explored early on and dropped from scope. Only download this if you want to
explore `dataset_pipeline/dataset_analysis.ipynb`'s full comparison across all three datasets.
Source: search "PlantDoc Dataset" on Kaggle (multiple mirrors exist; any should work for the
analysis notebook, which only reads folder/class structure).

## 3. Produce the balanced ("final") datasets

Run `dataset_pipeline/dataset_balancing.ipynb` top to bottom. This reads from `data/raw/` and
writes the balanced outputs into `data/final/`:

- `plantvillage_balanced/` — category-wise balancing, 2,000 images/class × 39 classes
- `plantvillage_balanced_by_plant/` — plant-species-wise balancing (a rejected alternative;
  produced for comparison, not used by any shipped model — see
  `experiments/TUNING_NOTES.md` for why)
- `new_plant_diseases_balanced/` — 2,300 images/class × 38 classes

This step uses `ImageDataGenerator`-based augmentation to top up under-represented classes —
expect it to take a while depending on your machine (it's CPU-bound image I/O, not GPU work).

## 4. Verify before running anything else

Before running any model training/inference notebook, run the verification script:

```bash
python check_data_setup.py
```

This checks folder presence, class-folder names, and rough expected image counts — it will
catch a wrong download or a missed combine step in seconds, rather than you finding out an hour
into a training run.

## 5. Notes

- `data/raw/`, `data/final/`, and the optional `plantdoc_raw/` are never committed to this repo
  (see `.gitignore`). If you fork this repo, you are expected to rebuild `data/` locally using
  this document.
- All dataset path references in the notebooks go through `dataset_config.py`
  (`RAW_DIR`, `FINAL_DIR`) — you should not need to edit any notebook to point at your local
  data, as long as it's placed exactly as described above.

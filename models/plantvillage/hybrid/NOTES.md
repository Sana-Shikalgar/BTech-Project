# Note on metrics.xlsx sheet naming

The original source file (`Hybrid/PlantVillage/metrics_hybrid_model_d02.xlsx`, produced by
`Hybrid/PlantVillage/D02-hybrid-efficientNetB0.ipynb`) has its `validation` and `test` sheets
swapped relative to how the project report (Table 6.5, Chapter 6) labels them:

- The sheet the notebook calls `validation` actually contains the numbers the report calls
  **Test** (Accuracy/Precision/Recall/F1 = 99.82% each; per-class detail includes
  `Corn___Northern_Leaf_Blight` recall = 96.5%, matching the report's stated lowest test-set
  per-class accuracy).
- The sheet the notebook calls `test` actually contains the numbers the report calls
  **Validation** (Accuracy/Precision/Recall/F1 = 99.72% each).

This copy (`models/plantvillage/hybrid/metrics.xlsx`) has had its sheet **names** swapped
(`validation` <-> `test`) so that the sheet named `validation` now holds the validation numbers
and the sheet named `test` now holds the test numbers, consistent with the report's labeling.
No cell data was changed — only the two sheet-tab names were exchanged.

The original file at `Hybrid/PlantVillage/metrics_hybrid_model_d02.xlsx` is untouched and still
has the original (swapped) labeling.

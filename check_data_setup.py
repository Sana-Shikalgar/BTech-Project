"""
Verifies that data/ is set up correctly before running any notebook.

Checks folder presence, class-folder names, and rough expected image counts.
Does not open or validate individual image files — only directory structure and counts.

Usage:
    python check_data_setup.py
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "data"
RAW_DIR = DATA_ROOT / "raw"
FINAL_DIR = DATA_ROOT / "final"

# Ground truth class lists, taken directly from the project's own verified local dataset
# (not from the Kaggle listing page, which may differ slightly in ordering/formatting).
PLANTVILLAGE_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Background_without_leaves", "Blueberry___healthy", "Cherry___Powdery_mildew",
    "Cherry___healthy", "Corn___Cercospora_leaf_spot Gray_leaf_spot", "Corn___Common_rust",
    "Corn___Northern_Leaf_Blight", "Corn___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy", "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot",
    "Peach___healthy", "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy",
    "Soybean___healthy", "Squash___Powdery_mildew", "Strawberry___Leaf_scorch",
    "Strawberry___healthy", "Tomato___Bacterial_spot", "Tomato___Early_blight",
    "Tomato___Late_blight", "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy",
]

NEW_PLANT_DISEASES_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy", "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_", "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy", "Grape___Black_rot", "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


def count_images(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(1 for f in folder.rglob("*") if f.suffix in IMAGE_EXTENSIONS)


def check_folder(label: str, folder: Path, expected_classes: list[str] | None = None,
                  expected_total: int | None = None, tolerance: float = 0.05) -> bool:
    print(f"\n[{label}]")
    print(f"  path: {folder}")

    if not folder.exists():
        print("  FAIL: folder does not exist")
        return False

    ok = True

    if expected_classes is not None:
        actual = {p.name for p in folder.iterdir() if p.is_dir()}
        expected = set(expected_classes)
        missing = expected - actual
        unexpected = actual - expected
        if missing:
            print(f"  FAIL: missing {len(missing)} expected class folder(s): {sorted(missing)[:5]}"
                  f"{' ...' if len(missing) > 5 else ''}")
            ok = False
        if unexpected:
            print(f"  WARN: {len(unexpected)} unexpected folder(s) found (not necessarily an "
                  f"error, just flagging): {sorted(unexpected)[:5]}"
                  f"{' ...' if len(unexpected) > 5 else ''}")
        if not missing:
            print(f"  OK: all {len(expected)} expected class folders present")

    total = count_images(folder)
    print(f"  image count: {total}")
    if expected_total is not None:
        lower, upper = expected_total * (1 - tolerance), expected_total * (1 + tolerance)
        if lower <= total <= upper:
            print(f"  OK: within {int(tolerance*100)}% of expected ({expected_total})")
        else:
            print(f"  FAIL: expected ~{expected_total} (+/-{int(tolerance*100)}%), got {total}")
            ok = False

    return ok


def main():
    print("Checking data/ setup against expected structure...")
    results = []

    results.append(check_folder(
        "raw/plantvillage_raw",
        RAW_DIR / "plantvillage_raw",
        expected_classes=PLANTVILLAGE_CLASSES,
        expected_total=61486,
    ))

    results.append(check_folder(
        "raw/new_plant_diseases_raw",
        RAW_DIR / "new_plant_diseases_raw",
        expected_classes=NEW_PLANT_DISEASES_CLASSES,
        expected_total=87900,
    ))

    # PlantDoc is optional — check presence only, don't fail the run if absent.
    plantdoc_dir = RAW_DIR / "plantdoc_raw"
    if plantdoc_dir.exists():
        check_folder("raw/plantdoc_raw (optional)", plantdoc_dir)
    else:
        print("\n[raw/plantdoc_raw (optional)]\n  not present — fine, only needed for the "
              "full dataset_analysis.ipynb comparison, not for any shipped model")

    results.append(check_folder(
        "final/plantvillage_balanced",
        FINAL_DIR / "plantvillage_balanced",
        expected_classes=PLANTVILLAGE_CLASSES,
        expected_total=78000,  # 2000/class x 39 classes
    ))

    # Plant-wise balancing does not target a uniform per-class count (that's the whole reason
    # it was rejected), so we only check the folder/classes exist, not an exact total.
    plantvillage_by_plant = FINAL_DIR / "plantvillage_balanced_by_plant"
    if plantvillage_by_plant.exists():
        check_folder(
            "final/plantvillage_balanced_by_plant (rejected alt., not required)",
            plantvillage_by_plant,
            expected_classes=PLANTVILLAGE_CLASSES,
        )
    else:
        print("\n[final/plantvillage_balanced_by_plant]\n  not present — fine, this was a "
              "rejected balancing approach, not used by any shipped model")

    results.append(check_folder(
        "final/new_plant_diseases_balanced",
        FINAL_DIR / "new_plant_diseases_balanced",
        expected_classes=NEW_PLANT_DISEASES_CLASSES,
        expected_total=87400,  # 2300/class x 38 classes
    ))

    print("\n" + "=" * 50)
    if all(results):
        print("All required checks passed. You're set up correctly.")
    else:
        print("Some required checks failed — see FAIL lines above before running any notebook.")
    print("=" * 50)


if __name__ == "__main__":
    main()
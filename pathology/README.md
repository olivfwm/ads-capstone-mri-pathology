# Pathology Branch: Sample Slide Feasibility Study

Notebooks for preparing H&E whole-slide images and comparing pathology foundation model encoders, developed on the five sample patients provided by the UChicago Departments of Radiology and Pathology. Part of the capstone project *Multimodal MRI-Pathology Framework for Precision Prostate Cancer Detection* (see the repository README).

## Status

These notebooks were built and run on the five sample patients (pt104, pt107, pt109, pt111, pt112), the five lowest-numbered IRB13 cases. All five have an MRI file; four have a slide. Only **pt109** was usable end to end:

| Patient | Outcome |
| --- | --- |
| pt104 | Rejected. Two nested ink loops; the lab attributed this to a radiologist error. |
| pt107 | Unusable. Damaged file, with 64% of tiles unreadable. |
| pt109 | Used for all results below. Clear marks, 579 tumor tiles. |
| pt111 | No slide provided. |
| pt112 | No labels. No ink marks on the section. |

For the full cohort, the lab performs tiling and ink tile exclusion, so notebooks 01 and 02 do not need to be rerun at scale. They document how the approach was developed and validated.

## Run order

| # | Notebook | Purpose | Runtime |
| --- | --- | --- | --- |
| 01 | `01_slide_eda_ink_regions.ipynb` | Slide exploration, ink detection on thumbnails, tumor region outlines, tissue tile grid | CPU |
| 02 | `02_tile_labeling_ink_exclusion.ipynb` | High-resolution ink recheck and tile labels (tumor, benign, excluded) | CPU |
| 03 | `03_encoder_comparison_uni_conch.ipynb` | UNI and CONCH feature extraction, linear probes, CONCH zero-shot | GPU (T4) |
| 04 | `04_encoder_checks_ink_buffer_regions.ipynb` | Checks for ink leakage, benign buffer width, and per-region scores | CPU |

Each notebook needs the outputs of the one before it. In every notebook: run the install cell, restart the session, then run from the Drive mount cell onward.

## Setup

* **Environment:** Google Colab with Google Drive mounted.
* **Data folder:** every notebook reads from `DATA_DIR = '/content/drive/MyDrive/spring/capstone/data'`. Edit this line if your data is elsewhere.
* **Slides:** OME-TIFF files named `{patient}.ome.tif` (e.g. `pt109.ome.tif`) in `DATA_DIR`. The lab converted these from the original Olympus `.vsi` scans.
* **Notebook 03 only:** a GPU runtime (Runtime > Change runtime type > T4 GPU), approved Hugging Face access to `MahmoodLab/UNI` and `MahmoodLab/conch`, and a Hugging Face token saved as the Colab secret `HF_TOKEN`.
* **Packages:** listed in the repository's `requirements.txt`. Each notebook's install cell installs what it needs.

## Notebooks

### 01: Slide exploration and ink regions

Loads each slide, builds a thumbnail 2,000 px wide (about 17 µm per pixel), and defines tumor regions from the pathologist's blue ink. Splits the tissue into a grid of 128 µm tiles.

1. **Ink mask:** hue 0.50 to 0.70, saturation ≥ 0.50, brightness > 0.15; specks under 15 px dropped.
2. **Edge ink removed:** a component counts as edge ink if at least 60% of it lies within 12 px of the tissue edge and it is elongated (length/width ≥ 3) or large (≥ 400 px).
3. **Grouping:** ink is dilated by a disk of radius 35 px (about 0.6 mm); marks that touch form one group, so dots up to about 1.2 mm apart join.
4. **Closing:** morphological closing with the same disk (dilate, then erode), implemented with distance transforms for an exact circular kernel. An earlier version with a radius 15 disk left rings broken.
5. **Region per group:** if filling the closed shape encloses at least 400 px, the filled ring is the region; otherwise the region is the convex hull of the group's ink (at least 2 separate marks).
6. **Cleanup:** drop regions under 300 px, and small regions (< 1% of tissue) lying mostly near the edge (≥ 50% within 40 px). Flag regions nested inside another region or covering more than 30% of the tissue.

On pt109, all three regions came from the convex hull path. On pt104, the loops never closed because some gaps were wider than about 1.2 mm.

**Outputs** (`eda_v4_outputs/`):

* `{pt}_tiles.csv`: one row per tile with full-resolution position (`x0`, `y0`), size (`tile_px`), tissue fraction (`tissue_frac`), whether it touches ink on the thumbnail (`touches_ink`), and the tumor region it falls in (`region_id`, or -1 if none)
* `{pt}_regions.csv`: one row per ink region, with any flags for ambiguous regions
* `{pt}_thumb.png` and the ink QA figure

### 02: Tile labeling and ink exclusion

At thumbnail scale a tile is only about 7 pixels wide, so small ink marks can be missed. This notebook rechecks every tissue tile at pyramid level 1 (about 1.4 µm per pixel) and assigns a label.

**Key settings**

| Setting | Value | Meaning |
| --- | --- | --- |
| `TILE_UM` | 128 | Tile side length in µm |
| `MIN_TISSUE` | 0.5 | Tiles with less than 50% tissue are dropped |
| `INK_H`, `INK_S` | hue 0.50 to 0.70, saturation ≥ 0.50 | Blue ink color rule (HSV) |
| `INK_FRAC_THRESH` | 0.002 | A tile touches ink if more than 0.2% of its pixels are ink |
| `BENIGN_MARGIN_UM` | 1000 | Benign tiles must be at least 1 mm from any ink region |

**Labels**

| Label | Meaning |
| --- | --- |
| `tumor` | Inside an ink region |
| `benign_presumed` | Outside all ink regions and at least 1 mm away from them |
| `excluded_ink` | Touches ink in either the thumbnail or the high-resolution check |
| `excluded_buffer` | Outside regions but within 1 mm of one |
| `uncertain` | Inside a region flagged as ambiguous |
| `pending` | Slide whose tumor location needs lab confirmation |
| `excluded_unreadable` | Image data damaged at every pyramid level tried |

Unmarked tissue is not confirmed benign: the pathologist marked only tumors on each section. The 1 mm margin keeps benign tiles away from tumor edges.

**Outputs** (`tiles_v1/`): `{pt}_tile_labels.csv` (one row per tissue tile with label, high-resolution ink fraction, and distance to the nearest ink region), `summary.csv`, and figures with sample tiles per label and a label map per slide. An optional cell exports tile images as 256 px JPEGs.

### 03: Encoder comparison (UNI vs CONCH)

Compares two frozen pathology foundation models on pt109's tiles. With one slide, this checks that the pipeline runs end to end and compares the encoders on the same tiles; it does not measure generalization to new patients.

1. **Tile selection:** all 579 tumor tiles and a random sample of 5,000 benign tiles (`N_BENIGN`; using all 26,555 is about 5 times slower).
2. **Feature extraction:** UNI (1,024 features per tile at 224 px) and CONCH (512 features per tile at 448 px).
3. **PCA plot** of each encoder's features, colored by label.
4. **Linear probe:** logistic regression on each encoder's features. Tiles are grouped into spatial blocks of about 2 mm (16 tiles) so nearby tiles stay in the same fold, and evaluated with 5-fold grouped cross-validation using pooled out-of-fold scores.
5. **CONCH zero-shot:** tiles are scored against text prompts for cancer and benign tissue, with no training.
6. **Prediction maps** on the slide, and the highest-scoring tumor and benign tiles for each model.

**Outputs** (`encoders_v1/`): `pt109_uni.npz` and `pt109_conch.npz` (features with tile coordinates and labels), `results.csv`, and figures.

### 04: Encoder checks

Reuses the saved features from 03 (no GPU, no re-extraction). Three checks:

1. **Ink leakage:** whether tumor tiles are bluer than benign ones, which could let the model detect leftover ink instead of tissue. Measures faint blue per tile, tests whether it alone separates the classes, and retrains without blue tiles and without tiles next to ink.
2. **Buffer width:** retrains with benign tiles at least 1, 2, and 3 mm from any tumor region, and plots benign tile scores against distance from the tumor.
3. **Per-region scores:** mean tumor score for each marked tumor region.

**Outputs** (`encoders_v1/`): `check_tint.csv`, `check_buffer.csv`, `check_regions.csv`, and figures.

## Results on pt109

Average precision chance level is 0.104 (the tumor share); AUC chance level is 0.5.

| Model | AUC | Balanced accuracy | Average precision |
| --- | --- | --- | --- |
| UNI linear probe | 0.917 | 0.797 | 0.655 |
| CONCH linear probe | 0.874 | 0.787 | 0.526 |
| CONCH zero-shot | 0.731 | 0.636 | 0.267 |

* Ink leakage was not detected: faint blue alone gave AUC 0.527, and removing blue tiles or tiles next to ink did not lower scores.
* A wider benign buffer raised UNI average precision from 0.655 (1 mm) to 0.840 (3 mm). This partly reflects removing the hardest benign tiles, not only cleaner labels.
* Two of three tumor regions scored well; one scored low, possibly because its ink outline encloses a large share of stroma.
* UNI outperformed CONCH in every check.

## Data handling

Slides, tile tables, features, and patient spreadsheets are not stored in this repository. Do not commit them, and do not upload patient data to online tools without lab approval.

## Next steps

For the full cohort, this branch produces one pathology vector per lesion for `fusion/`: UNI features for the lab's cohort tiles, averaged within each lesion (ABMIL later), saved as `path_lesions.npz` keyed by `lesion_id`.

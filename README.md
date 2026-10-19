# Multimodal MRI-Pathology Framework for Precision Prostate Cancer Detection

Capstone project for the MS in Applied Data Science, University of Chicago, in collaboration with the UChicago Departments of Radiology and Pathology.

**Team:** Dhanush Ramachandran, Olivia Fang, Mahima Goyal

**Supervisor:** Utku Pamuksuz

## Overview

Prostate cancer is diagnosed from two sources read separately: MRI, which shows where a tumor is, and pathology, which shows how aggressive it is. This project links the two at the level of individual tumors (lesions) and predicts whether each lesion is clinically significant (Gleason grade group 2 or higher) from both modalities together.

Each lesion is identified by a shared key, `lesion_id = irb{IRB}_pat{case}_c{cancer_number}` (e.g. `irb13_pat109_c1`), which links its MRI outline, its pathology tiles, and its Gleason grade.

```
mpMRI + lesion outlines  ->  MRI vector per lesion  ----------\
                                                                join on lesion_id -> fusion -> P(GG2+) per lesion
H&E slide tiles -> UNI -> pathology vector per lesion  -------/                               + risk rank within patient
```

## Repository structure

```
README.md                 this file
requirements.txt          Python packages for all folders
.gitignore                keeps patient data out of the repository
pathology/                pathology branch: ink handling, tiling, UNI vs CONCH encoder comparison
mri/                      MRI branch (in progress)
fusion/                   concatenation fusion baseline, GG1 vs GG2+
scripts/                  cohort descriptives and paper figures
```

| Folder | Contents | Owner |
| --- | --- | --- |
| `pathology/` | Notebooks 01 to 04: slide exploration and ink regions, tile labeling, encoder comparison, encoder checks | Olivia Fang |
| `mri/` | MRI preprocessing and encoder | Mahima Goyal |
| `fusion/` | `fusion_baseline_concat.ipynb`: MRI only, pathology only, and concatenated models | Olivia Fang |
| `scripts/` | `gleason_distribution.py` (grade distribution of the paired cohort), `pipeline_diagram.py` (architecture figure) | Olivia Fang |

Each folder has its own README with inputs, outputs, and run instructions.

## Status

| Component | Status |
| --- | --- |
| Pathology feasibility study | Done on the one usable sample slide (pt109). UNI outperformed CONCH; see `pathology/README.md`. |
| Cohort tiling and ink tile exclusion | Done by the lab for the full cohort |
| Cohort pathology vectors (UNI per lesion) | Next |
| MRI lesion vectors | In progress |
| Fusion baseline | Implemented; runs in demo mode on synthetic data until both lesion vectors exist |
| ABMIL, MRI encoder, cross-attention | Planned |

## Data

The analysis cohort has 53 cases (20 from IRB13-0756, 33 from IRB18-1681) with mpMRI, radiologist lesion outlines, whole-mount H&E slides, and pathologist Gleason grades, for 163 tumors in total, 115 of them outlined on MRI.

**No patient data is stored in this repository.** Slides, MRI files, spreadsheets, features, and derived outputs stay on lab storage. The `.gitignore` blocks the common file types; check `git status` before every commit.

## Setup

```bash
pip install -r requirements.txt
```

* `pathology/` notebooks run in Google Colab with Google Drive mounted; notebook 03 needs a GPU and Hugging Face access to UNI and CONCH.
* `fusion/` and `scripts/` read lab spreadsheets with patient case numbers, so run them on the lab cluster or locally, not in Colab.

### Scripts

```bash
# Grade distribution figure and table (set the two spreadsheet paths at the top first)
python3 scripts/gleason_distribution.py

# Architecture figure
python3 scripts/pipeline_diagram.py
```

# Fusion

Combines one MRI vector and one pathology vector per lesion to predict **GG1 vs GG2+** (clinically significant cancer).

## `fusion_baseline_concat.ipynb`

Trains three logistic regressions on the same patient-level split (MRI only, pathology only, MRI + pathology) for **GG1 vs GG2+** per lesion, following the agreed evaluation design: patient-level 70/15/15 split, C tuned on validation macro F1, test lesions scored once. Metrics are accuracy (read against the majority-class rate), macro F1, and a within-patient risk ranking score. Quadratic weighted kappa is added if the target becomes three ordered classes (GG1, GG2, GG3+).

**Status:** runs in demo mode (`DEMO = True`) on synthetic lesions shaped like the cohort. Demo numbers only confirm the pipeline runs.

**Interface.** Every input is keyed by `lesion_id = irb{IRB}_pat{case}_c{cancer_number}`, e.g. `irb13_pat109_c1`.

| Input | Format | Content |
| --- | --- | --- |
| MRI lesion vectors | CSV: `lesion_id` + feature columns | One MRI vector per lesion. Stand-in until the MRI encoder exists: mean and SD of ADC and T2 inside the lesion outline. |
| Pathology lesion vectors | `.npz` with `lesion_id` and `features` (n_lesions × 1024) | Mean of the UNI tile vectors inside each lesion. `pool_tiles()` builds this from tile features. |
| Master log | `.xlsx` | Gleason scores, converted to grade groups and the GG2+ label |

Lesions missing from either modality are dropped and reported. The pathology vector is reduced to 16 principal components (fitted on training lesions only) so it doesn't outweigh the few MRI features. Run on the cluster or locally, not Colab, since the master log contains patient case numbers. Set `DEMO = False` and the three input paths in the Settings cell once real inputs exist.

## Core model (designed, next to implement)

The concatenation notebook is the **baseline**. The core model, as described in the paper, has two stages:

1. **Contrastive alignment:** small projection heads (encoders frozen) map MRI and pathology vectors into a shared space, trained with InfoNCE so the same lesion's two representations lie close together. The heads are then applied to the token vectors.
2. **Cross-attention fusion:** MRI voxel tokens and pathology tile tokens attend over each other; the pooled output feeds the GG1 vs GG2+ classifier, whose scores also rank lesions within each patient.

Needs: per-voxel MRI features (`mri/README.md`) and per-tile UNI features for each lesion. Its value is measured against the concatenation baseline, and alignment is evaluated by comparing the core model with and without it.

## Other options

* **ABMIL pathology summary vectors** in place of mean pooling.
* **Three-class target** (GG1, GG2, GG3+), evaluated with quadratic weighted kappa.

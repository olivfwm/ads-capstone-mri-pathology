# Fusion

Combines one MRI vector and one pathology vector per lesion to predict **GG1 vs GG2+** (clinically significant cancer).

## `fusion_baseline_concat.ipynb`

Trains three logistic regressions on the same patient-level splits (MRI only, pathology only, MRI + pathology) for **GG1 vs GG2+** per lesion, and reports AUC, average precision, balanced accuracy, F1, and a within-patient risk ranking score, on a 70/15/15 test split and with 5-fold patient-grouped cross-validation.

**Status:** runs in demo mode (`DEMO = True`) on synthetic lesions shaped like the cohort. Demo numbers only confirm the pipeline runs.

**Interface.** Every input is keyed by `lesion_id = irb{IRB}_pat{case}_c{cancer_number}`, e.g. `irb13_pat109_c1`.

| Input | Format | Content |
| --- | --- | --- |
| MRI lesion vectors | CSV: `lesion_id` + feature columns | One MRI vector per lesion. Stand-in until the MRI encoder exists: mean and SD of ADC and T2 inside the lesion outline. |
| Pathology lesion vectors | `.npz` with `lesion_id` and `features` (n_lesions × 1024) | Mean of the UNI tile vectors inside each lesion. `pool_tiles()` builds this from tile features. |
| Master log | `.xlsx` | Gleason scores, converted to grade groups and the GG2+ label |

Lesions missing from either modality are dropped and reported. The pathology vector is reduced to 16 principal components (fitted on training lesions only) so it doesn't outweigh the few MRI features. Run on the cluster or locally, not Colab, since the master log contains patient case numbers. Set `DEMO = False` and the three input paths in the Settings cell once real inputs exist.

## Planned

* **ABMIL pathology vectors** in place of mean pooling.
* **MRI encoder embeddings** in place of the ADC/T2 stand-in.
* **Cross-attention fusion**, adopted only if it beats this baseline under the same evaluation.

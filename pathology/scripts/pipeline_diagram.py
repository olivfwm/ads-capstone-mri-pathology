import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
fig, ax = plt.subplots(figsize=(17.5, 6.2))
ax.set_xlim(0, 214); ax.set_ylim(0, 62); ax.axis("off")
MRI, PATH, CORE, BASE = "#f3e0e0", "#e6e9f2", "#efefef", "#ffffff"

def box(x, y, w, h, title, sub, color, dashed=False, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                 fc=color, ec="#444444", lw=1.1, ls="--" if dashed else "-"))
    ax.text(x + w/2, y + h*0.68, title, ha="center", va="center", fontsize=11, weight="bold" if bold else "normal")
    ax.text(x + w/2, y + h*0.30, sub, ha="center", va="center", fontsize=9, linespacing=1.25)

def arrow(x1, y1, x2, y2, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                 lw=1.2, color="#444444", ls="--" if dashed else "-", shrinkA=0, shrinkB=0))

# MRI branch
box(1, 44, 26, 12, "mpMRI", "T2 and ADC +\nradiologist lesion outlines", MRI)
box(33, 44, 28, 12, "MRI encoder", "nnU-Net features\n(stand-in: ADC and T2 statistics)", MRI)
box(67, 44, 26, 12, "MRI features", "voxel tokens +\nsummary vector", MRI)
arrow(27.8, 50, 32.2, 50); arrow(61.8, 50, 66.2, 50)
# Pathology branch
box(1, 6, 26, 12, "H&E slide tiles", "128 µm tiles per lesion;\nink tiles excluded (lab)", PATH)
box(33, 6, 28, 12, "UNI (frozen)", "1,024 features per tile", PATH)
box(67, 6, 26, 12, "Pathology features", "tile tokens + summary\nvector (mean; later ABMIL)", PATH)
arrow(27.8, 12, 32.2, 12); arrow(61.8, 12, 66.2, 12)
# Join and core path
box(99, 25, 22, 12, "Join", "on lesion ID\n(study, case, cancer #)", CORE)
arrow(93.8, 50, 100, 37.6); arrow(93.8, 12, 100, 24.4)
box(127, 34, 28, 12, "Contrastive alignment", "projection heads;\nsame lesion pulled together", CORE)
box(161, 34, 28, 12, "Cross-attention fusion", "each modality attends\nover the other's tokens", CORE)
arrow(121.8, 34, 126.2, 38); arrow(155.8, 40, 160.2, 40)
# Baseline path
box(127, 12, 62, 11, "Baseline: concatenation", "summary vectors joined; logistic regression", BASE, dashed=True)
arrow(121.8, 28, 126.2, 20, dashed=True)
# Output
box(197, 22, 16, 16, "Output", "P(GG2+) per\nlesion; risk\nrank within\npatient", CORE)
arrow(189.8, 40, 196.2, 36); arrow(189.8, 17.5, 196.2, 24, dashed=True)
ax.text(14, 59, "MRI branch", fontsize=11, style="italic", ha="center")
ax.text(14, 2, "Pathology branch", fontsize=11, style="italic", ha="center")
plt.savefig("pipeline_diagram.png", dpi=300, bbox_inches="tight")

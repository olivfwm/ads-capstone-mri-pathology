import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
fig, ax = plt.subplots(figsize=(15, 5.4))
ax.set_xlim(0, 158); ax.set_ylim(0, 52); ax.axis("off")
MRI, PATH, JOIN, DASH = "#f3e0e0", "#e6e9f2", "#efefef", "#ffffff"

def box(x, y, w, h, title, sub, color, dashed=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                 fc=color, ec="#444444", lw=1.1, ls="--" if dashed else "-"))
    ax.text(x + w/2, y + h*0.66, title, ha="center", va="center", fontsize=11, weight="bold")
    ax.text(x + w/2, y + h*0.30, sub, ha="center", va="center", fontsize=9, linespacing=1.25)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                 lw=1.2, color="#444444", shrinkA=0, shrinkB=0))

# MRI branch (top)
box(1, 34, 24, 12, "mpMRI", "image volumes +\nradiologist lesion outlines", MRI)
box(31, 34, 24, 12, "MRI lesion features", "stand-in: ADC and T2\nmean and SD per lesion", MRI)
box(61, 34, 22, 12, "MRI vector", "one per lesion\n(later: MRI encoder)", MRI, dashed=False)
arrow(25.8, 40, 30.2, 40); arrow(55.8, 40, 60.2, 40)
# Pathology branch (bottom)
box(1, 6, 24, 12, "H&E slide tiles", "128 µm tiles in each lesion;\nink tiles excluded (lab)", PATH)
box(31, 6, 24, 12, "UNI (frozen)", "1,024 features\nper tile", PATH)
box(61, 6, 22, 12, "Pathology vector", "mean of tile vectors\n(later: ABMIL)", PATH)
arrow(25.8, 12, 30.2, 12); arrow(55.8, 12, 60.2, 12)
# Join, fusion, output
box(90, 20, 20, 12, "Join", "on lesion ID\n(study, case, cancer #)", JOIN)
arrow(83.8, 40, 91, 32.6); arrow(83.8, 12, 91, 19.4)
box(116, 29, 18, 11, "Concatenation", "baseline:\nlogistic regression", JOIN)
box(116, 12, 18, 11, "Cross-attention", "planned", DASH, dashed=True)
arrow(110.8, 28, 115.2, 33); arrow(110.8, 24, 115.2, 18)
box(139, 19, 18, 14, "Output", "P(GG2+) per lesion;\nrisk rank within\npatient", JOIN)
arrow(134.8, 34, 138.2, 29); arrow(134.8, 17, 138.2, 23)
ax.text(13, 49.5, "MRI branch", fontsize=11, style="italic", ha="center")
ax.text(13, 2, "Pathology branch", fontsize=11, style="italic", ha="center")
plt.savefig("pipeline_diagram.png", dpi=300, bbox_inches="tight")

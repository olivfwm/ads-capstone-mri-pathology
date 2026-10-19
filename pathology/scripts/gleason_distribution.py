"""Gleason grade distribution for the paired cohort.

Inputs (from the "70 case (ERC) database_Roger's project" folder):
  Master_Log_IRB1318      one row per tumor: case, cancer number, location, Gleason score, size
  drawn_cancer_information which tumors the radiologist outlined on MRI, per case

Output: figures/gleason_distribution.png, tumor counts by grade group,
split into outlined on MRI vs not outlined, for the cases that have MRI outlines.

Run locally or on the cluster. These sheets contain patient identifiers, so do not
upload them to online tools.
"""
import re
import pandas as pd
import matplotlib.pyplot as plt

# Set to the full paths of the two lab spreadsheets (on the IRB13-0756 volume)
MASTER = "path/to/Master_Log_IRB1318.xlsx"
DRAWN = "path/to/drawn_cancer_information.xlsx"

# 1. Load and print the columns
master = pd.read_excel(MASTER)
drawn = pd.read_excel(DRAWN)
print(master.columns.tolist())
print(drawn.columns.tolist())

# 2. Find columns by name, ignoring capitalization, extra spaces, and line breaks
def find_col(df, *words):
    for c in df.columns:
        name = " ".join(str(c).lower().split())
        if all(w in name for w in words):
            return c
    raise KeyError(f"No column containing {words}. Columns: {df.columns.tolist()}")

M_IRB = find_col(master, "irb")
M_CASE = find_col(master, "case")
M_CANCER = find_col(master, "cancer #")
M_GLEASON = find_col(master, "gleason")
D_CASE = find_col(drawn, "case name")
D_DRAWN = find_col(drawn, "drawn cancer indices")

# 3. Parse "7 (4+3) with small 5" into primary and secondary patterns, then grade group
def grade_group(text):
    m = re.search(r"(\d)\s*\+\s*(\d)", str(text))
    if not m:
        return None
    p, s = int(m.group(1)), int(m.group(2))
    total = p + s
    if total <= 6:
        return 1
    if total == 7:
        return 2 if p == 3 else 3
    return 4 if total == 8 else 5

master = master.dropna(subset=[M_CASE, M_CANCER]).copy()
master["irb"] = master[M_IRB].apply(lambda x: str(int(float(x))))
master["case"] = master[M_CASE].apply(lambda x: str(int(float(x))))
master["cancer"] = master[M_CANCER].apply(lambda x: int(float(x)))
master["grade_group"] = master[M_GLEASON].apply(grade_group)
unparsed = master[master.grade_group.isna()]
print(f"{len(unparsed)} tumors with unparsed Gleason scores:")
print(unparsed[[M_IRB, M_CASE, M_CANCER, M_GLEASON]])

# 4. Mark which tumors were outlined on MRI. Case names look like "irb13_pat104";
#    the drawn column lists cancer numbers like "1,2".
outlined, drawn_cases = set(), set()
for _, r in drawn.iterrows():
    m = re.search(r"irb(\d+)_pat(\d+)", str(r[D_CASE]).lower())
    if not m:
        continue
    irb, case = str(int(m.group(1))), str(int(m.group(2)))
    drawn_cases.add((irb, case))
    for n in re.findall(r"\d+", str(r[D_DRAWN])):
        outlined.add((irb, case, int(n)))

master["key"] = list(zip(master.irb, master.case))
cohort = master[master.key.isin(drawn_cases) & master.grade_group.notna()].copy()
cohort["outlined"] = [(i, c, n) in outlined for i, c, n in zip(cohort.irb, cohort.case, cohort.cancer)]
print(f"{cohort.key.nunique()} cases, {len(cohort)} tumors, {cohort.outlined.sum()} outlined on MRI")
missing = drawn_cases - set(master.key)
if missing:
    print(f"{len(missing)} cases in the drawn sheet have no rows in the master log: {sorted(missing)}")

# 5. Table for the paper and stacked bar chart
counts = (cohort.groupby(["grade_group", "outlined"]).size()
          .unstack(fill_value=0).reindex(range(1, 6), fill_value=0))
counts = counts.reindex(columns=[True, False], fill_value=0)
counts.columns = ["Outlined on MRI", "Not outlined"]
print(counts)
counts.to_csv("gleason_distribution_table.csv")

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
labels = ["GG1\n(3+3)", "GG2\n(3+4)", "GG3\n(4+3)", "GG4\n(8)", "GG5\n(9 to 10)"]
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.bar(labels, counts["Outlined on MRI"], color="#800000", label="Outlined on MRI")
ax.bar(labels, counts["Not outlined"], bottom=counts["Outlined on MRI"], color="#cccccc", label="Not outlined")
for i, total in enumerate(counts.sum(axis=1)):
    ax.text(i, total + 1, str(total), ha="center", fontsize=10)
ax.set_xlabel("Grade group (Gleason score)")
ax.set_ylabel("Number of tumors")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("gleason_distribution.png", dpi=300)   # no title: the caption goes in the paper
plt.show()

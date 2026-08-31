import csv
import os
import random

# ============================================================
# SETTINGS
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CSV_FILE = os.path.join(
    PROJECT_DIR,
    "cnn",
    "cnn_labels.csv"
)

random.seed(42)

# ============================================================
# LABEL OPTIONS
# ============================================================

growth_labels = ["early", "mid", "late"]
leaf_labels = ["sparse", "moderate", "dense"]
branch_labels = ["none", "developing", "developed"]

# ============================================================
# GROWTH-AWARE DISTRIBUTIONS
# ============================================================

growth_distribution = {
    "week_1": {
        "early": 0.90,
        "mid": 0.10,
        "late": 0.00
    },

    "week_2": {
        "early": 0.15,
        "mid": 0.75,
        "late": 0.10
    },

    "week_3": {
        "early": 0.05,
        "mid": 0.25,
        "late": 0.70
    }
}

leaf_distribution = {
    "week_1": {
        "sparse": 0.75,
        "moderate": 0.25,
        "dense": 0.00
    },

    "week_2": {
        "sparse": 0.20,
        "moderate": 0.65,
        "dense": 0.15
    },

    "week_3": {
        "sparse": 0.05,
        "moderate": 0.35,
        "dense": 0.60
    }
}

branch_distribution = {
    "week_1": {
        "none": 0.95,
        "developing": 0.05,
        "developed": 0.00
    },

    "week_2": {
        "none": 0.40,
        "developing": 0.55,
        "developed": 0.05
    },

    "week_3": {
        "none": 0.05,
        "developing": 0.35,
        "developed": 0.60
    }
}

# ============================================================
# RANDOM SELECTION FUNCTION
# ============================================================

def choose_label(distribution):
    labels = list(distribution.keys())
    probabilities = list(distribution.values())

    return random.choices(
        labels,
        weights=probabilities,
        k=1
    )[0]

# ============================================================
# LOAD CSV
# ============================================================

with open(
    CSV_FILE,
    "r",
    newline="",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)
    rows = list(reader)

# ============================================================
# GENERATE PROVISIONAL LABELS
# ============================================================

for row in rows:

    week = row["image_path"].split("/")[0]

    row["overall_growth"] = choose_label(
        growth_distribution[week]
    )

    row["leaf_distribution"] = choose_label(
        leaf_distribution[week]
    )

    row["branch_development"] = choose_label(
        branch_distribution[week]
    )

# ============================================================
# SAVE
# ============================================================

fieldnames = [
    "image_path",
    "group",
    "overall_growth",
    "leaf_distribution",
    "branch_development"
]

with open(
    CSV_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)

print("============================================")
print("PROVISIONAL LABELING COMPLETED")
print("============================================")
print(f"Images labeled: {len(rows)}")
print(f"CSV: {CSV_FILE}")
print("")
print("WARNING:")
print("These labels are synthetic/provisional.")
print("They must not be reported as manually observed")
print("ground-truth labels in the research.")
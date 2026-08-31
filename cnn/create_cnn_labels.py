import os
import csv

# ============================================================
# PATHS
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_DIR = os.path.join(
    PROJECT_DIR,
    "dataset"
)

OUTPUT_FILE = os.path.join(
    PROJECT_DIR,
    "cnn",
    "cnn_labels.csv"
)


# ============================================================
# DATASET SETTINGS
# ============================================================

weeks = ["week_1", "week_2", "week_3"]

groups = {
    "exposed": "EXP",
    "controlled": "CTL"
}


# ============================================================
# CREATE CSV
# ============================================================

rows = []

for week in weeks:

    for group, code in groups.items():

        folder = os.path.join(
            DATASET_DIR,
            week,
            group
        )

        if not os.path.exists(folder):
            print(f"WARNING: Folder not found: {folder}")
            continue

        files = sorted(
            [
                file
                for file in os.listdir(folder)
                if file.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".jfif")
                )
            ]
        )

        for file in files:

            image_path = os.path.join(
                week,
                group,
                file
            ).replace("\\", "/")

            rows.append([
                image_path,
                group,
                "",
                "",
                ""
            ])


# ============================================================
# SAVE CSV
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "image_path",
        "group",
        "overall_growth",
        "leaf_distribution",
        "branch_development"
    ])

    writer.writerows(rows)


# ============================================================
# RESULT
# ============================================================

print("\n============================================")
print("CNN LABEL FILE CREATED")
print("============================================")

print(f"Total images: {len(rows)}")

print("\nCSV saved to:")
print(OUTPUT_FILE)

print("\nThe following columns still need labels:")
print("1. overall_growth")
print("2. leaf_distribution")
print("3. branch_development")
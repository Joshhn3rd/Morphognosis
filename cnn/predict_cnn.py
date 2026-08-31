import os
import json
import sys
import re
import numpy as np
import tensorflow as tf

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


# ============================================================
# 1. PROJECT PATHS
# ============================================================

CNN_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_FOLDER = os.path.dirname(
    CNN_FOLDER
)

MODEL_PATH = os.path.join(
    PROJECT_FOLDER,
    "saved_models",
    "mobilenetv2_plant_analysis.keras"
)

CLASS_PATH = os.path.join(
    PROJECT_FOLDER,
    "saved_models",
    "mobilenetv2_plant_analysis_classes.json"
)


# ============================================================
# 2. SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)


# ============================================================
# 3. STRUCTURAL INTERPRETATION THRESHOLDS
# ============================================================
#
# These values convert the predicted numerical structure
# into the corresponding structural categories.
#
# Adjust these thresholds after checking your actual
# 12-month plant growth dataset.
#

HEIGHT_EARLY_MAX = 10.0
HEIGHT_MID_MAX = 20.0

LEAVES_SPARSE_MAX = 3
LEAVES_MODERATE_MAX = 7

BRANCH_NONE_MAX = 0
BRANCH_DEVELOPING_MAX = 2


# ============================================================
# 4. CHECK MODEL AND CLASS FILE
# ============================================================

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"\nCNN model not found:\n{MODEL_PATH}"
    )

if not os.path.exists(CLASS_PATH):

    raise FileNotFoundError(
        f"\nClass mapping not found:\n{CLASS_PATH}"
    )


# ============================================================
# 5. LOAD CNN MODEL
# ============================================================

print("\n============================================")
print("LOADING MORPHOGNOSIS CNN")
print("============================================")

model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# 6. LOAD CLASS MAPPING
# ============================================================

with open(
    CLASS_PATH,
    "r",
    encoding="utf-8"
) as file:

    class_mapping = json.load(file)


# ============================================================
# 7. CHECK CNN OUTPUT CLASSES
# ============================================================

required_outputs = [
    "overall_growth",
    "leaf_distribution",
    "branch_development"
]

for output_name in required_outputs:

    if output_name not in class_mapping:

        raise KeyError(
            f"\nMissing class mapping for: {output_name}"
        )


print("\nAvailable CNN classes:")

for output_name in required_outputs:

    print(f"\n{output_name}:")

    for index, label in class_mapping[
        output_name
    ].items():

        print(
            f"  {index} = {label}"
        )


# ============================================================
# 8. GET IMAGE PATH
# ============================================================

if len(sys.argv) > 1:

    image_path = sys.argv[1]

else:

    image_path = input(
        "\nEnter the path of the plant image: "
    ).strip()


image_path = image_path.strip(
    '"'
).strip(
    "'"
)


# ============================================================
# 9. RESOLVE IMAGE PATH
# ============================================================

if os.path.isabs(image_path):

    resolved_image_path = os.path.normpath(
        image_path
    )

else:

    resolved_image_path = os.path.normpath(
        os.path.join(
            PROJECT_FOLDER,
            image_path
        )
    )


# ============================================================
# 10. CHECK IMAGE
# ============================================================

if not os.path.exists(
    resolved_image_path
):

    print("\n============================================")
    print("IMAGE NOT FOUND")
    print("============================================")

    print("\nPython searched for:")
    print(resolved_image_path)

    print("\nEntered path:")
    print(image_path)

    print("\nProject folder:")
    print(PROJECT_FOLDER)

    raise FileNotFoundError(
        "\nThe image path does not exist."
    )


print("\nImage found:")
print(resolved_image_path)


# ============================================================
# 11. DETECT MONTH
# ============================================================
#
# Dataset naming:
#
# week_1 = Month 1
# week_2 = Month 2
# week_3 = Month 3
#

month = None

match = re.search(
    r"week[_-]?(\d+)",
    image_path.lower()
)

if match:

    month = int(
        match.group(1)
    )


# ============================================================
# 12. GET PREDICTED STRUCTURAL DATA
# ============================================================
#
# The values should come from your computational
# growth prediction model.
#
# Command-line example:
#
# python predict_cnn.py image.jpg 23.0 8 4
#
# Meaning:
#
# image.jpg = image
# 23.0       = predicted height
# 8          = predicted leaves
# 4          = predicted branches
#

if len(sys.argv) >= 5:

    try:

        predicted_height = float(
            sys.argv[2]
        )

        predicted_leaves = int(
            sys.argv[3]
        )

        predicted_branches = int(
            sys.argv[4]
        )

    except ValueError:

        raise ValueError(
            "\nInvalid structural prediction values.\n"
            "Expected:\n"
            "height leaves branches\n"
            "Example: 23.0 8 4"
        )

else:

    print("\n============================================")
    print("PREDICTED PLANT STRUCTURE")
    print("============================================")

    predicted_height = float(
        input(
            "Predicted height (cm): "
        ).strip()
    )

    predicted_leaves = int(
        input(
            "Predicted number of leaves: "
        ).strip()
    )

    predicted_branches = int(
        input(
            "Predicted number of branches: "
        ).strip()
    )


# ============================================================
# 13. VALIDATE STRUCTURAL DATA
# ============================================================

if predicted_height < 0:

    raise ValueError(
        "Predicted height must not be negative."
    )

if predicted_leaves < 0:

    raise ValueError(
        "Predicted leaf count must not be negative."
    )

if predicted_branches < 0:

    raise ValueError(
        "Predicted branch count must not be negative."
    )


# ============================================================
# 14. STRUCTURAL INTERPRETATION FUNCTION
# ============================================================

def interpret_structure(
    height,
    leaves,
    branches
):

    # --------------------------------------------------------
    # OVERALL GROWTH
    # --------------------------------------------------------

    if height <= HEIGHT_EARLY_MAX:

        overall = "early"

    elif height <= HEIGHT_MID_MAX:

        overall = "mid"

    else:

        overall = "late"


    # --------------------------------------------------------
    # LEAF DISTRIBUTION
    # --------------------------------------------------------

    if leaves <= LEAVES_SPARSE_MAX:

        leaf = "sparse"

    elif leaves <= LEAVES_MODERATE_MAX:

        leaf = "moderate"

    else:

        leaf = "dense"


    # --------------------------------------------------------
    # BRANCH DEVELOPMENT
    # --------------------------------------------------------

    if branches <= BRANCH_NONE_MAX:

        branch = "none"

    elif branches <= BRANCH_DEVELOPING_MAX:

        branch = "developing"

    else:

        branch = "developed"


    return (
        overall,
        leaf,
        branch
    )


# ============================================================
# 15. GENERATE STRUCTURAL INTERPRETATION
# ============================================================

structural_overall, structural_leaf, structural_branch = \
    interpret_structure(
        predicted_height,
        predicted_leaves,
        predicted_branches
    )


# ============================================================
# 16. LOAD IMAGE
# ============================================================

print("\nProcessing image...")

image = tf.keras.utils.load_img(
    resolved_image_path,
    target_size=IMAGE_SIZE
)

image_array = tf.keras.utils.img_to_array(
    image
)

image_array = np.expand_dims(
    image_array,
    axis=0
)

image_array = preprocess_input(
    image_array
)


# ============================================================
# 17. CNN PREDICTION
# ============================================================

predictions = model.predict(
    image_array,
    verbose=0
)


# ============================================================
# 18. GET THREE CNN OUTPUTS
# ============================================================

try:

    overall_prediction = predictions[
        "overall_growth"
    ][0]

    leaf_prediction = predictions[
        "leaf_distribution"
    ][0]

    branch_prediction = predictions[
        "branch_development"
    ][0]

except Exception as error:

    raise RuntimeError(
        "\nThe CNN model outputs do not match the "
        "expected output names.\n\n"
        "Expected outputs:\n"
        "overall_growth\n"
        "leaf_distribution\n"
        "branch_development\n\n"
        f"Actual model output:\n{predictions}"
    ) from error


# ============================================================
# 19. GET CLASS INFORMATION
# ============================================================

def get_class_result(
    prediction,
    mapping
):

    prediction = np.asarray(
        prediction
    ).flatten()

    sorted_indices = np.argsort(
        prediction
    )[::-1]

    results = []

    for index in sorted_indices:

        index = int(index)

        if str(index) not in mapping:

            continue

        label = mapping[
            str(index)
        ]

        confidence = (
            float(prediction[index]) * 100
        )

        results.append(
            (
                label,
                confidence
            )
        )

    if not results:

        raise ValueError(
            "\nNo valid class mapping was found."
        )

    best_index = int(
        sorted_indices[0]
    )

    best_label = mapping[
        str(best_index)
    ]

    best_confidence = (
        float(prediction[best_index]) * 100
    )

    return (
        best_label,
        best_confidence,
        results
    )


# ============================================================
# 20. GET CNN PREDICTIONS
# ============================================================

cnn_overall_label, \
cnn_overall_confidence, \
overall_all = get_class_result(
    overall_prediction,
    class_mapping["overall_growth"]
)


cnn_leaf_label, \
cnn_leaf_confidence, \
leaf_all = get_class_result(
    leaf_prediction,
    class_mapping["leaf_distribution"]
)


cnn_branch_label, \
cnn_branch_confidence, \
branch_all = get_class_result(
    branch_prediction,
    class_mapping["branch_development"]
)


# ============================================================
# 21. DISPLAY MAIN RESULT
# ============================================================

print("\n============================================")
print("      MORPHOGNOSIS PLANT IMAGE ANALYSIS")
print("============================================")

print("\nImage:")
print(
    os.path.basename(
        resolved_image_path
    )
)


# ============================================================
# 22. DISPLAY GROWTH PERIOD
# ============================================================

if month is not None:

    print("\nGrowth Period:")
    print(
        f"Month {month}"
    )


# ============================================================
# 23. DISPLAY PREDICTED PLANT STRUCTURE
# ============================================================

print("\n============================================")
print("PREDICTED PLANT STRUCTURE")
print("============================================")

print(
    f"Height: {predicted_height:.2f} cm"
)

print(
    f"Leaves: {predicted_leaves}"
)

print(
    f"Branches: {predicted_branches}"
)


# ============================================================
# 24. STRUCTURAL INTERPRETATION
# ============================================================

print("\n============================================")
print("STRUCTURAL INTERPRETATION")
print("============================================")

print(
    f"Overall Growth: "
    f"{structural_overall.title()}"
)

print(
    f"Leaf Distribution: "
    f"{structural_leaf.title()}"
)

print(
    f"Branch Development: "
    f"{structural_branch.title()}"
)


# ============================================================
# 25. CNN VISUAL CLASSIFICATION
# ============================================================

print("\n============================================")
print("CNN VISUAL CLASSIFICATION")
print("============================================")

print(
    f"Overall Growth: "
    f"{cnn_overall_label.title()} "
    f"({cnn_overall_confidence:.2f}%)"
)

print(
    f"Leaf Distribution: "
    f"{cnn_leaf_label.title()} "
    f"({cnn_leaf_confidence:.2f}%)"
)

print(
    f"Branch Development: "
    f"{cnn_branch_label.title()} "
    f"({cnn_branch_confidence:.2f}%)"
)


# ============================================================
# 26. SHOW ALL CNN CLASS PROBABILITIES
# ============================================================

print("\n============================================")
print("CNN CLASS PROBABILITIES")
print("============================================")


print("\nOVERALL GROWTH:")

for label, confidence in overall_all:

    print(
        f"{label.title():<15}"
        f"{confidence:>7.2f}%"
    )


print("\nLEAF DISTRIBUTION:")

for label, confidence in leaf_all:

    print(
        f"{label.title():<15}"
        f"{confidence:>7.2f}%"
    )


print("\nBRANCH DEVELOPMENT:")

for label, confidence in branch_all:

    print(
        f"{label.title():<15}"
        f"{confidence:>7.2f}%"
    )


# ============================================================
# 27. FINAL GROWTH INTERPRETATION
# ============================================================

print("\n============================================")
print("FINAL GROWTH INTERPRETATION")
print("============================================")

print(
    "The structural interpretation is based on "
    "the predicted plant measurements."
)

print(
    f"\nThe predicted height of "
    f"{predicted_height:.2f} cm corresponds to "
    f"{structural_overall} growth."
)

print(
    f"The predicted leaf count of "
    f"{predicted_leaves} corresponds to "
    f"{structural_leaf} leaf distribution."
)

print(
    f"The predicted branch count of "
    f"{predicted_branches} corresponds to "
    f"{structural_branch} branch development."
)


# ============================================================
# 28. COMPLETE SUMMARY
# ============================================================

print("\n============================================")
print("MORPHOGNOSIS SUMMARY")
print("============================================")

print(
    f"Height: "
    f"{predicted_height:.2f} cm"
)

print(
    f"Leaves: "
    f"{predicted_leaves}"
)

print(
    f"Branches: "
    f"{predicted_branches}"
)

print(
    f"\nOverall Growth: "
    f"{structural_overall.title()}"
)

print(
    f"Leaf Distribution: "
    f"{structural_leaf.title()}"
)

print(
    f"Branch Development: "
    f"{structural_branch.title()}"
)


# ============================================================
# 29. COMPLETED
# ============================================================

print("\n============================================")
print("ANALYSIS COMPLETED")
print("============================================")
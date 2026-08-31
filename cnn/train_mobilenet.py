import os
import csv
import json
import random
import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


# ============================================================
# 1. PROJECT PATHS
# ============================================================

# Current file:
# morphognosis/cnn/train_mobilenet.py

CNN_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

# morphognosis/
PROJECT_FOLDER = os.path.dirname(
    CNN_FOLDER
)

# Dataset:
# morphognosis/dataset/

DATASET_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "dataset"
)

# CSV:
# morphognosis/cnn/cnn_labels.csv

CSV_PATH = os.path.join(
    CNN_FOLDER,
    "cnn_labels.csv"
)

# Saved models:
# morphognosis/saved_models/

MODEL_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "saved_models"
)

MODEL_PATH = os.path.join(
    MODEL_FOLDER,
    "mobilenetv2_plant_analysis.keras"
)

CLASS_PATH = os.path.join(
    MODEL_FOLDER,
    "mobilenetv2_plant_analysis_classes.json"
)


# ============================================================
# 2. SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)

BATCH_SIZE = 8

EPOCHS = 15

VALIDATION_SPLIT = 0.20

SEED = 42

random.seed(SEED)


# ============================================================
# 3. LABEL DEFINITIONS
# ============================================================

OVERALL_GROWTH_LABELS = [
    "early",
    "mid",
    "late"
]

LEAF_DISTRIBUTION_LABELS = [
    "sparse",
    "moderate",
    "dense"
]

BRANCH_DEVELOPMENT_LABELS = [
    "none",
    "developing",
    "developed"
]


# Create numeric mappings

OVERALL_GROWTH_MAP = {
    label: index
    for index, label
    in enumerate(OVERALL_GROWTH_LABELS)
}

LEAF_DISTRIBUTION_MAP = {
    label: index
    for index, label
    in enumerate(LEAF_DISTRIBUTION_LABELS)
}

BRANCH_DEVELOPMENT_MAP = {
    label: index
    for index, label
    in enumerate(BRANCH_DEVELOPMENT_LABELS)
}


# ============================================================
# 4. HEADER
# ============================================================

print("\n============================================")
print("MOBILENETV2 PLANT ANALYSIS CNN")
print("============================================")

print("\nDataset folder:")
print(DATASET_FOLDER)

print("\nCSV label file:")
print(CSV_PATH)


# ============================================================
# 5. CHECK FILES
# ============================================================

if not os.path.exists(DATASET_FOLDER):

    raise FileNotFoundError(
        f"\nDataset folder not found:\n{DATASET_FOLDER}"
    )


if not os.path.exists(CSV_PATH):

    raise FileNotFoundError(
        f"\nCNN label CSV not found:\n{CSV_PATH}"
    )


# ============================================================
# 6. READ CSV
# ============================================================

print("\n============================================")
print("READING CNN LABELS")
print("============================================")

image_paths = []

overall_labels = []

leaf_labels = []

branch_labels = []

groups = []


with open(
    CSV_PATH,
    "r",
    newline="",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    required_columns = [
        "image_path",
        "group",
        "overall_growth",
        "leaf_distribution",
        "branch_development"
    ]

    for column in required_columns:

        if column not in reader.fieldnames:

            raise ValueError(
                f"Missing CSV column: {column}"
            )


    for row in reader:

        image_path = row[
            "image_path"
        ].strip()

        group = row[
            "group"
        ].strip()

        overall = row[
            "overall_growth"
        ].strip().lower()

        leaf = row[
            "leaf_distribution"
        ].strip().lower()

        branch = row[
            "branch_development"
        ].strip().lower()


        # Check labels are not empty

        if not overall or not leaf or not branch:

            raise ValueError(
                f"\nMissing label for image:\n"
                f"{image_path}"
            )


        # Check labels are valid

        if overall not in OVERALL_GROWTH_MAP:

            raise ValueError(
                f"Invalid overall growth label "
                f"'{overall}' in {image_path}"
            )


        if leaf not in LEAF_DISTRIBUTION_MAP:

            raise ValueError(
                f"Invalid leaf distribution label "
                f"'{leaf}' in {image_path}"
            )


        if branch not in BRANCH_DEVELOPMENT_MAP:

            raise ValueError(
                f"Invalid branch development label "
                f"'{branch}' in {image_path}"
            )


        # Convert relative path to full path

        full_image_path = os.path.join(
            DATASET_FOLDER,
            image_path
        )


        if not os.path.exists(
            full_image_path
        ):

            raise FileNotFoundError(
                f"\nImage not found:\n"
                f"{full_image_path}"
            )


        image_paths.append(
            full_image_path
        )

        overall_labels.append(
            OVERALL_GROWTH_MAP[overall]
        )

        leaf_labels.append(
            LEAF_DISTRIBUTION_MAP[leaf]
        )

        branch_labels.append(
            BRANCH_DEVELOPMENT_MAP[branch]
        )

        groups.append(
            group
        )


print(
    f"\nTotal images found: "
    f"{len(image_paths)}"
)


# ============================================================
# 7. CHECK IMAGE COUNT
# ============================================================

if len(image_paths) == 0:

    raise ValueError(
        "\nNo images were found in the CSV."
    )


# ============================================================
# 8. SHUFFLE AND SPLIT DATA
# ============================================================

print("\n============================================")
print("CREATING TRAINING / VALIDATION SPLIT")
print("============================================")


indices = list(
    range(len(image_paths))
)

random.shuffle(indices)


validation_count = max(
    1,
    int(
        len(indices)
        * VALIDATION_SPLIT
    )
)


validation_indices = indices[
    :validation_count
]

training_indices = indices[
    validation_count:
]


def select_items(
    items,
    indices
):

    return [
        items[index]
        for index in indices
    ]


train_paths = select_items(
    image_paths,
    training_indices
)

val_paths = select_items(
    image_paths,
    validation_indices
)


train_overall = select_items(
    overall_labels,
    training_indices
)

val_overall = select_items(
    overall_labels,
    validation_indices
)


train_leaf = select_items(
    leaf_labels,
    training_indices
)

val_leaf = select_items(
    leaf_labels,
    validation_indices
)


train_branch = select_items(
    branch_labels,
    training_indices
)

val_branch = select_items(
    branch_labels,
    validation_indices
)


print(
    f"Training images: "
    f"{len(train_paths)}"
)

print(
    f"Validation images: "
    f"{len(val_paths)}"
)


# ============================================================
# 9. IMAGE LOADING FUNCTION
# ============================================================

def load_image(
    image_path,
    overall,
    leaf,
    branch
):

    image = tf.io.read_file(
        image_path
    )

    image = tf.image.decode_jpeg(
        image,
        channels=3
    )

    image = tf.image.resize(
        image,
        IMAGE_SIZE
    )

    image = tf.cast(
        image,
        tf.float32
    )


    labels = {
        "overall_growth": overall,
        "leaf_distribution": leaf,
        "branch_development": branch
    }


    return image, labels


# ============================================================
# 10. CREATE TF.DATA DATASETS
# ============================================================

train_dataset = tf.data.Dataset.from_tensor_slices(
    (
        train_paths,
        train_overall,
        train_leaf,
        train_branch
    )
)


validation_dataset = tf.data.Dataset.from_tensor_slices(
    (
        val_paths,
        val_overall,
        val_leaf,
        val_branch
    )
)


train_dataset = train_dataset.shuffle(
    buffer_size=len(train_paths),
    seed=SEED
)


train_dataset = train_dataset.map(
    load_image,
    num_parallel_calls=tf.data.AUTOTUNE
)


validation_dataset = validation_dataset.map(
    load_image,
    num_parallel_calls=tf.data.AUTOTUNE
)


train_dataset = train_dataset.batch(
    BATCH_SIZE
)


validation_dataset = validation_dataset.batch(
    BATCH_SIZE
)


train_dataset = train_dataset.prefetch(
    tf.data.AUTOTUNE
)


validation_dataset = validation_dataset.prefetch(
    tf.data.AUTOTUNE
)


# ============================================================
# 11. DATA AUGMENTATION
# ============================================================

data_augmentation = tf.keras.Sequential([

    layers.RandomFlip(
        "horizontal"
    ),

    layers.RandomRotation(
        0.10
    ),

    layers.RandomZoom(
        0.10
    )

])


# ============================================================
# 12. LOAD MOBILENETV2
# ============================================================

print("\n============================================")
print("LOADING PRETRAINED MOBILENETV2")
print("============================================")


base_model = MobileNetV2(

    input_shape=(
        224,
        224,
        3
    ),

    include_top=False,

    weights="imagenet"

)


# Freeze pretrained layers

base_model.trainable = False


print(
    "MobileNetV2 loaded successfully."
)


# ============================================================
# 13. BUILD MULTI-OUTPUT MODEL
# ============================================================

print("\n============================================")
print("BUILDING THREE-OUTPUT CNN")
print("============================================")


inputs = layers.Input(
    shape=(
        224,
        224,
        3
    )
)


# Augmentation

x = data_augmentation(
    inputs
)


# MobileNet preprocessing

x = preprocess_input(
    x
)


# Feature extraction

x = base_model(
    x,
    training=False
)


# Convert feature maps to vector

x = layers.GlobalAveragePooling2D()(x)


# Shared dropout

x = layers.Dropout(
    0.30
)(x)


# ============================================================
# OUTPUT 1 — OVERALL GROWTH
# ============================================================

overall_output = layers.Dense(
    3,
    activation="softmax",
    name="overall_growth"
)(x)


# ============================================================
# OUTPUT 2 — LEAF DISTRIBUTION
# ============================================================

leaf_output = layers.Dense(
    3,
    activation="softmax",
    name="leaf_distribution"
)(x)


# ============================================================
# OUTPUT 3 — BRANCH DEVELOPMENT
# ============================================================

branch_output = layers.Dense(
    3,
    activation="softmax",
    name="branch_development"
)(x)


# ============================================================
# FINAL MODEL
# ============================================================

model = models.Model(

    inputs=inputs,

    outputs={
        "overall_growth": overall_output,
        "leaf_distribution": leaf_output,
        "branch_development": branch_output
    }

)


# ============================================================
# 14. COMPILE
# ============================================================

model.compile(

    optimizer="adam",

    loss={
        "overall_growth":
            "sparse_categorical_crossentropy",

        "leaf_distribution":
            "sparse_categorical_crossentropy",

        "branch_development":
            "sparse_categorical_crossentropy"
    },

    metrics={
        "overall_growth":
            ["accuracy"],

        "leaf_distribution":
            ["accuracy"],

        "branch_development":
            ["accuracy"]
    }

)


# ============================================================
# 15. MODEL SUMMARY
# ============================================================

print("\n============================================")
print("MODEL SUMMARY")
print("============================================")

model.summary()


# ============================================================
# 16. TRAIN
# ============================================================

print("\n============================================")
print("STARTING TRAINING")
print("============================================")

history = model.fit(

    train_dataset,

    validation_data=validation_dataset,

    epochs=EPOCHS

)


# ============================================================
# 17. CREATE MODEL FOLDER
# ============================================================

os.makedirs(
    MODEL_FOLDER,
    exist_ok=True
)


# ============================================================
# 18. SAVE MODEL
# ============================================================

model.save(
    MODEL_PATH
)


# ============================================================
# 19. SAVE CLASS MAPPINGS
# ============================================================

class_mapping = {

    "overall_growth": {

        str(index): label

        for index, label
        in enumerate(
            OVERALL_GROWTH_LABELS
        )

    },

    "leaf_distribution": {

        str(index): label

        for index, label
        in enumerate(
            LEAF_DISTRIBUTION_LABELS
        )

    },

    "branch_development": {

        str(index): label

        for index, label
        in enumerate(
            BRANCH_DEVELOPMENT_LABELS
        )

    }

}


with open(
    CLASS_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        class_mapping,
        file,
        indent=4
    )


# ============================================================
# 20. FINAL RESULTS
# ============================================================

print("\n============================================")
print("TRAINING COMPLETED")
print("============================================")


print("\nModel saved to:")

print(
    MODEL_PATH
)


print("\nClass mapping saved to:")

print(
    CLASS_PATH
)


print("\nCNN outputs:")

print(
    "1. Overall Growth"
)

print(
    "2. Leaf Distribution"
)

print(
    "3. Branch Development"
)


print("\n============================================")
print("DONE")
print("============================================")
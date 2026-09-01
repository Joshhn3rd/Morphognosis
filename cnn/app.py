from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import os
import json
import numpy as np
import tensorflow as tf

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


app = Flask(__name__)
CORS(app)


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# 2. CNN MODEL PATH
# ============================================================

CNN_MODEL_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "mobilenetv2_plant_analysis.keras"
)


CNN_CLASS_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "mobilenetv2_plant_analysis_classes.json"
)


# ============================================================
# 3. LOAD CNN MODEL
# ============================================================

print("\n============================================")
print("LOADING MORPHOGNOSIS CNN SERVICE")
print("============================================")


if not os.path.exists(CNN_MODEL_PATH):

    raise FileNotFoundError(
        f"CNN model not found: {CNN_MODEL_PATH}"
    )


cnn_model = tf.keras.models.load_model(
    CNN_MODEL_PATH,
    compile=False
)


print("CNN model loaded successfully.")


# ============================================================
# 4. LOAD CLASS MAPPING
# ============================================================

if not os.path.exists(CNN_CLASS_PATH):

    raise FileNotFoundError(
        f"CNN class mapping not found: {CNN_CLASS_PATH}"
    )


with open(
    CNN_CLASS_PATH,
    "r",
    encoding="utf-8"
) as file:

    cnn_classes = json.load(file)


print("CNN class mapping loaded successfully.")


# ============================================================
# 5. HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "service": "Morphognosis CNN",
        "status": "online"
    })


# ============================================================
# 6. CNN IMAGE ANALYSIS
# ============================================================

def predict_plant_image(image_path):

    IMAGE_SIZE = (
        224,
        224
    )


    # --------------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------------

    image = tf.keras.utils.load_img(
        image_path,
        target_size=IMAGE_SIZE
    )


    # --------------------------------------------------------
    # IMAGE TO ARRAY
    # --------------------------------------------------------

    image_array = tf.keras.utils.img_to_array(
        image
    )


    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    # --------------------------------------------------------
    # MOBILENETV2 PREPROCESSING
    # --------------------------------------------------------

    image_array = preprocess_input(
        image_array
    )


    # --------------------------------------------------------
    # CNN PREDICTION
    # --------------------------------------------------------

    predictions = cnn_model(
    image_array,
    training=False
    )


    # ========================================================
    # HANDLE MODEL OUTPUT
    # ========================================================

    if isinstance(
        predictions,
        dict
    ):

        overall_prediction = predictions[
            "overall_growth"
        ][0]

        leaf_prediction = predictions[
            "leaf_distribution"
        ][0]

        branch_prediction = predictions[
            "branch_development"
        ][0]


    elif isinstance(
        predictions,
        list
    ):

        overall_prediction = predictions[0][0]

        leaf_prediction = predictions[1][0]

        branch_prediction = predictions[2][0]


    else:

        raise RuntimeError(
            "Unexpected CNN output format."
        )


    # ========================================================
    # CLASS INDICES
    # ========================================================

    overall_index = int(
        np.argmax(
            overall_prediction
        )
    )


    leaf_index = int(
        np.argmax(
            leaf_prediction
        )
    )


    branch_index = int(
        np.argmax(
            branch_prediction
        )
    )


    # ========================================================
    # CLASS LABELS
    # ========================================================

    cnn_growth = cnn_classes[
        "overall_growth"
    ][
        str(overall_index)
    ]


    cnn_leaf = cnn_classes[
        "leaf_distribution"
    ][
        str(leaf_index)
    ]


    cnn_branch = cnn_classes[
        "branch_development"
    ][
        str(branch_index)
    ]


    # ========================================================
    # CONFIDENCE
    # ========================================================

    growth_confidence = (

        float(
            overall_prediction[
                overall_index
            ]
        )

        * 100
    )


    leaf_confidence = (

        float(
            leaf_prediction[
                leaf_index
            ]
        )

        * 100
    )


    branch_confidence = (

        float(
            branch_prediction[
                branch_index
            ]
        )

        * 100
    )


    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "overallGrowth":
            cnn_growth,

        "overallGrowthConfidence":
            round(
                growth_confidence,
                2
            ),

        "leafDistribution":
            cnn_leaf,

        "leafDistributionConfidence":
            round(
                leaf_confidence,
                2
            ),

        "branchDevelopment":
            cnn_branch,

        "branchDevelopmentConfidence":
            round(
                branch_confidence,
                2
            )

    }


    # ========================================================
    # TERMINAL OUTPUT
    # ========================================================

    print("\n============================================")
    print("CNN IMAGE ANALYSIS")
    print("============================================")


    print(
        "Growth:",
        cnn_growth,
        f"({growth_confidence:.2f}%)"
    )


    print(
        "Leaf Distribution:",
        cnn_leaf,
        f"({leaf_confidence:.2f}%)"
    )


    print(
        "Branch Development:",
        cnn_branch,
        f"({branch_confidence:.2f}%)"
    )


    return result


# ============================================================
# 7. ANALYZE IMAGE API
# ============================================================

@app.route(
    "/analyze_image",
    methods=["POST"]
)
def analyze_image():

    print("\n============================================")
    print("CNN IMAGE REQUEST")
    print("============================================")


    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    if "plantImage" not in request.files:

        return jsonify({
            "error": "No plant image uploaded."
        }), 400


    image = request.files[
        "plantImage"
    ]


    if image.filename == "":

        return jsonify({
            "error": "No image selected."
        }), 400


    # --------------------------------------------------------
    # SECURE FILENAME
    # --------------------------------------------------------

    filename = secure_filename(
        image.filename
    )


    if not filename:

        return jsonify({
            "error": "Invalid image filename."
        }), 400


    # --------------------------------------------------------
    # UPLOAD DIRECTORY
    # --------------------------------------------------------

    upload_folder = os.path.join(
        BASE_DIR,
        "uploads"
    )


    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # --------------------------------------------------------
    # IMAGE PATH
    # --------------------------------------------------------

    image_path = os.path.join(
        upload_folder,
        filename
    )


    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    image.save(
        image_path
    )


    print(
        "Image received:",
        filename
    )


    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    try:

        result = predict_plant_image(
            image_path
        )


        return jsonify(
            result
        )


    except Exception as e:

        print("\nCNN ERROR")
        print(str(e))


        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# 8. START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
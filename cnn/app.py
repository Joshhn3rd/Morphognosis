from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import os
import json
import numpy as np
from PIL import Image
from ai_edge_litert.interpreter import Interpreter


app = Flask(__name__)
CORS(app)


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# 2. TFLITE MODEL PATHS
# ============================================================

TFLITE_MODEL_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "mobilenetv2_plant_analysis.tflite"
)

CNN_CLASS_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "mobilenetv2_plant_analysis_classes.json"
)


# ============================================================
# 3. LOAD TFLITE MODEL
# ============================================================

print("\n============================================")
print("LOADING MORPHOGNOSIS TFLITE SERVICE")
print("============================================")

if not os.path.exists(TFLITE_MODEL_PATH):
    raise FileNotFoundError(
        f"TFLite model not found: {TFLITE_MODEL_PATH}"
    )


interpreter = Interpreter(
    model_path=TFLITE_MODEL_PATH,
    num_threads=1
)

interpreter.allocate_tensors()


# Get model information
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

signature_list = interpreter.get_signature_list()

print("TFLite model loaded successfully.")
print("Input:", input_details)
print("Outputs:", output_details)
print("Signatures:", signature_list)


# Make sure expected signature exists
if "serving_default" not in signature_list:
    raise RuntimeError(
        "Expected TFLite signature 'serving_default' was not found."
    )


# Create named signature runner
signature_runner = interpreter.get_signature_runner(
    "serving_default"
)


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
        "service": "Morphognosis TFLite CNN",
        "status": "online"
    })


# ============================================================
# 6. TFLITE IMAGE ANALYSIS
# ============================================================

def predict_plant_image(image_path):

    # --------------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")


    # --------------------------------------------------------
    # RESIZE TO MOBILENETV2 INPUT SIZE
    # --------------------------------------------------------

    image = image.resize(
        (224, 224)
    )


    # --------------------------------------------------------
    # CONVERT IMAGE TO NUMPY ARRAY
    # --------------------------------------------------------

    image_array = np.asarray(
        image,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # MOBILENETV2 PREPROCESSING
    #
    # Equivalent to:
    # tensorflow.keras.applications.mobilenet_v2.preprocess_input
    #
    # Converts pixel values:
    # 0..255 -> -1..1
    # --------------------------------------------------------

    image_array = (
        image_array / 127.5
    ) - 1.0


    # Add batch dimension:
    # (224, 224, 3)
    # ->
    # (1, 224, 224, 3)

    image_array = np.expand_dims(
        image_array,
        axis=0
    ).astype(np.float32)


    # ========================================================
    # RUN TFLITE INFERENCE
    #
    # Our converted model confirmed this signature:
    #
    # input:
    # input_layer_1
    #
    # outputs:
    # branch_development
    # leaf_distribution
    # overall_growth
    # ========================================================

    outputs = signature_runner(
        input_layer_1=image_array
    )


    # --------------------------------------------------------
    # GET NAMED OUTPUTS
    # --------------------------------------------------------

    overall_prediction = outputs[
        "overall_growth"
    ][0]

    leaf_prediction = outputs[
        "leaf_distribution"
    ][0]

    branch_prediction = outputs[
        "branch_development"
    ][0]


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
    ][str(overall_index)]


    cnn_leaf = cnn_classes[
        "leaf_distribution"
    ][str(leaf_index)]


    cnn_branch = cnn_classes[
        "branch_development"
    ][str(branch_index)]


    # ========================================================
    # CONFIDENCE SCORES
    # ========================================================

    growth_confidence = float(
        overall_prediction[
            overall_index
        ]
    ) * 100


    leaf_confidence = float(
        leaf_prediction[
            leaf_index
        ]
    ) * 100


    branch_confidence = float(
        branch_prediction[
            branch_index
        ]
    ) * 100


    # ========================================================
    # JSON RESULT
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
    # SERVER LOG
    # ========================================================

    print("\n============================================")
    print("TFLITE IMAGE ANALYSIS")
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

    print("============================================")


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
    print("TFLITE IMAGE REQUEST")
    print("============================================")


    # --------------------------------------------------------
    # CHECK IMAGE EXISTS
    # --------------------------------------------------------

    if "plantImage" not in request.files:

        return jsonify({
            "error":
                "No plant image uploaded."
        }), 400


    image = request.files[
        "plantImage"
    ]


    # --------------------------------------------------------
    # CHECK FILE NAME
    # --------------------------------------------------------

    if image.filename == "":

        return jsonify({
            "error":
                "No image selected."
        }), 400


    filename = secure_filename(
        image.filename
    )


    if not filename:

        return jsonify({
            "error":
                "Invalid image filename."
        }), 400


    # --------------------------------------------------------
    # CREATE UPLOAD DIRECTORY
    # --------------------------------------------------------

    upload_folder = os.path.join(
        BASE_DIR,
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    image_path = os.path.join(
        upload_folder,
        filename
    )


    # --------------------------------------------------------
    # SAVE IMAGE TEMPORARILY
    # --------------------------------------------------------

    image.save(
        image_path
    )


    print(
        "Image received:",
        filename
    )


    # --------------------------------------------------------
    # RUN MODEL
    # --------------------------------------------------------

    try:

        result = predict_plant_image(
            image_path
        )

        return jsonify(
            result
        )


    except Exception as e:

        print("\n============================================")
        print("TFLITE ERROR")
        print("============================================")
        print(str(e))

        return jsonify({
            "error": str(e)
        }), 500


    # --------------------------------------------------------
    # DELETE TEMPORARY UPLOAD
    # --------------------------------------------------------

    finally:

        try:

            if os.path.exists(
                image_path
            ):
                os.remove(
                    image_path
                )

        except Exception as cleanup_error:

            print(
                "Upload cleanup warning:",
                cleanup_error
            )


# ============================================================
# 8. START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
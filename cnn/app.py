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
# 2. TFLITE MODEL PATH
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

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("TFLite model loaded successfully.")
print("Input:", input_details)
print("Outputs:", output_details)
print("Signatures:", interpreter.get_signature_list())


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
    # LOAD + RESIZE IMAGE
    # --------------------------------------------------------

    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))

    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # MOBILENETV2 PREPROCESSING
    # Equivalent to preprocess_input()
    # Converts 0..255 -> -1..1
    # --------------------------------------------------------

    image_array = (
        image_array / 127.5
    ) - 1.0

    image_array = np.expand_dims(
        image_array,
        axis=0
    ).astype(np.float32)


    # --------------------------------------------------------
    # RUN TFLITE INFERENCE
    # --------------------------------------------------------

    interpreter.set_tensor(
        input_details[0]["index"],
        image_array
    )

    interpreter.invoke()


    # --------------------------------------------------------
    # GET ALL THREE OUTPUTS
    # --------------------------------------------------------

    outputs = {}

    for detail in output_details:

        output_value = interpreter.get_tensor(
            detail["index"]
        )[0]

        output_name = detail["name"].lower()

        if "overall" in output_name:
            outputs["overall_growth"] = output_value

        elif "leaf" in output_name:
            outputs["leaf_distribution"] = output_value

        elif "branch" in output_name:
            outputs["branch_development"] = output_value


    # --------------------------------------------------------
    # FALLBACK FOR OUTPUT ORDER
    # --------------------------------------------------------

    if len(outputs) != 3:

        raw_outputs = [
            interpreter.get_tensor(
                detail["index"]
            )[0]
            for detail in output_details
        ]

        outputs = {
            "overall_growth": raw_outputs[0],
            "leaf_distribution": raw_outputs[1],
            "branch_development": raw_outputs[2]
        }


    overall_prediction = outputs[
        "overall_growth"
    ]

    leaf_prediction = outputs[
        "leaf_distribution"
    ]

    branch_prediction = outputs[
        "branch_development"
    ]


    # ========================================================
    # CLASS INDICES
    # ========================================================

    overall_index = int(
        np.argmax(overall_prediction)
    )

    leaf_index = int(
        np.argmax(leaf_prediction)
    )

    branch_index = int(
        np.argmax(branch_prediction)
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
    # CONFIDENCE
    # ========================================================

    growth_confidence = float(
        overall_prediction[overall_index]
    ) * 100

    leaf_confidence = float(
        leaf_prediction[leaf_index]
    ) * 100

    branch_confidence = float(
        branch_prediction[branch_index]
    ) * 100


    # ========================================================
    # RESULT
    # ========================================================

    result = {
        "overallGrowth": cnn_growth,
        "overallGrowthConfidence": round(
            growth_confidence,
            2
        ),
        "leafDistribution": cnn_leaf,
        "leafDistributionConfidence": round(
            leaf_confidence,
            2
        ),
        "branchDevelopment": cnn_branch,
        "branchDevelopmentConfidence": round(
            branch_confidence,
            2
        )
    }


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

    if "plantImage" not in request.files:

        return jsonify({
            "error": "No plant image uploaded."
        }), 400

    image = request.files["plantImage"]

    if image.filename == "":

        return jsonify({
            "error": "No image selected."
        }), 400

    filename = secure_filename(
        image.filename
    )

    if not filename:

        return jsonify({
            "error": "Invalid image filename."
        }), 400

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

    image.save(
        image_path
    )

    print(
        "Image received:",
        filename
    )

    try:

        result = predict_plant_image(
            image_path
        )

        return jsonify(
            result
        )

    except Exception as e:

        print("\nTFLITE ERROR")
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
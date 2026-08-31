from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from models.hybrid_formula import HybridFormula
from models.predict_xgboost import predict_growth

import os
import json
import numpy as np
import tensorflow as tf

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


app = Flask(__name__)


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# 2. HYBRID FORMULA
# ============================================================

formula = HybridFormula()


# ============================================================
# 3. CNN MODEL PATHS
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
# 4. LOAD CNN MODEL
# ============================================================

print("\n============================================")
print("LOADING MORPHOGNOSIS CNN")
print("============================================")

if not os.path.exists(CNN_MODEL_PATH):

    print("WARNING: CNN model not found:")
    print(CNN_MODEL_PATH)

    cnn_model = None

else:

    cnn_model = tf.keras.models.load_model(
        CNN_MODEL_PATH
    )

    print("CNN model loaded successfully.")


# ============================================================
# 5. LOAD CNN CLASS MAPPING
# ============================================================

cnn_classes = None

if os.path.exists(CNN_CLASS_PATH):

    with open(
        CNN_CLASS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        cnn_classes = json.load(file)

    print("CNN class mapping loaded successfully.")

else:

    print("WARNING: CNN class mapping not found:")
    print(CNN_CLASS_PATH)


# ============================================================
# 6. HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.xhtml"
    )


# ============================================================
# 7. PREDICTION PAGE
# ============================================================

@app.route("/prediction")
def prediction():

    return render_template(
        "prediction.xhtml"
    )


# ============================================================
# 8. ENVIRONMENT PAGE
# ============================================================

@app.route("/environment")
def environment():

    return render_template(
        "environment.xhtml"
    )


# ============================================================
# 9. HISTORY PAGE
# ============================================================

@app.route("/history")
def history():

    return render_template(
        "history.xhtml"
    )


# ============================================================
# 10. NUMERICAL STRUCTURAL CLASSIFICATION
# ============================================================

def classify_growth(
    height,
    leaves,
    branches
):

    # --------------------------------------------------------
    # OVERALL GROWTH
    # --------------------------------------------------------

    if (
        height >= 20
        and leaves >= 7
    ):

        growth = "late"

    elif (
        height >= 10
        and leaves >= 4
    ):

        growth = "mid"

    else:

        growth = "early"


    # --------------------------------------------------------
    # LEAF DISTRIBUTION
    # --------------------------------------------------------

    if leaves >= 7:

        leaf = "dense"

    elif leaves >= 4:

        leaf = "moderate"

    else:

        leaf = "sparse"


    # --------------------------------------------------------
    # BRANCH DEVELOPMENT
    # --------------------------------------------------------

    if branches >= 4:

        branch = "developed"

    elif branches >= 1:

        branch = "developing"

    else:

        branch = "none"


    return (
        growth,
        leaf,
        branch
    )


# ============================================================
# 11. COMBINE NUMERICAL + CNN CLASSIFICATION
# ============================================================

def combine_analysis(

    numerical_growth,
    numerical_leaf,
    numerical_branch,

    cnn_growth,
    cnn_leaf,
    cnn_branch,

    cnn_growth_confidence,
    cnn_leaf_confidence,
    cnn_branch_confidence

):

    # --------------------------------------------------------
    # MODEL WEIGHTS
    # --------------------------------------------------------

    numerical_weight = 0.70
    cnn_weight = 0.30


    # --------------------------------------------------------
    # COMBINATION FUNCTION
    # --------------------------------------------------------

    def combine_category(

        numerical_value,
        cnn_value,
        cnn_confidence

    ):

        numerical_value = (
            numerical_value.lower()
        )

        cnn_value = (
            cnn_value.lower()
        )


        # ----------------------------------------------------
        # BOTH MODELS AGREE
        # ----------------------------------------------------

        if numerical_value == cnn_value:

            return (
                numerical_value,
                "agreement"
            )


        # ----------------------------------------------------
        # NUMERICAL MODEL SCORE
        # ----------------------------------------------------

        numerical_score = (
            numerical_weight
        )


        # ----------------------------------------------------
        # CNN SCORE
        # ----------------------------------------------------

        cnn_score = (

            cnn_weight

            *

            (
                cnn_confidence
                / 100
            )

        )


        # ----------------------------------------------------
        # DETERMINE DOMINANT RESULT
        # ----------------------------------------------------

        if numerical_score >= cnn_score:

            return (
                numerical_value,
                "numerical_dominant"
            )

        else:

            return (
                cnn_value,
                "cnn_dominant"
            )


    # ========================================================
    # GROWTH
    # ========================================================

    final_growth, growth_source = combine_category(

        numerical_growth,

        cnn_growth,

        cnn_growth_confidence

    )


    # ========================================================
    # LEAF DISTRIBUTION
    # ========================================================

    final_leaf, leaf_source = combine_category(

        numerical_leaf,

        cnn_leaf,

        cnn_leaf_confidence

    )


    # ========================================================
    # BRANCH DEVELOPMENT
    # ========================================================

    final_branch, branch_source = combine_category(

        numerical_branch,

        cnn_branch,

        cnn_branch_confidence

    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "growth":
            final_growth,

        "leaf":
            final_leaf,

        "branch":
            final_branch,

        "growthSource":
            growth_source,

        "leafSource":
            leaf_source,

        "branchSource":
            branch_source
    }


# ============================================================
# 12. CNN IMAGE PREDICTION
# ============================================================

def predict_plant_image(
    image_path
):

    # --------------------------------------------------------
    # CHECK CNN MODEL
    # --------------------------------------------------------

    if cnn_model is None:

        raise RuntimeError(
            "CNN model is not loaded."
        )


    # --------------------------------------------------------
    # CHECK CLASS MAPPING
    # --------------------------------------------------------

    if cnn_classes is None:

        raise RuntimeError(
            "CNN class mapping is not loaded."
        )


    IMAGE_SIZE = (
        224,
        224
    )


    # ========================================================
    # LOAD IMAGE
    # ========================================================

    image = tf.keras.utils.load_img(

        image_path,

        target_size=IMAGE_SIZE

    )


    # ========================================================
    # CONVERT IMAGE TO ARRAY
    # ========================================================

    image_array = tf.keras.utils.img_to_array(
        image
    )


    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    # ========================================================
    # MOBILENETV2 PREPROCESSING
    # ========================================================

    image_array = preprocess_input(
        image_array
    )


    # ========================================================
    # CNN PREDICTION
    # ========================================================

    predictions = cnn_model.predict(

        image_array,

        verbose=0

    )


    # ========================================================
    # HANDLE CNN OUTPUT
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
    # CNN CLASS INDICES
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
    # CNN LABELS
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
    # CNN CONFIDENCE
    # ========================================================

    cnn_growth_confidence = (

        float(
            overall_prediction[
                overall_index
            ]
        )

        * 100

    )


    cnn_leaf_confidence = (

        float(
            leaf_prediction[
                leaf_index
            ]
        )

        * 100

    )


    cnn_branch_confidence = (

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
                cnn_growth_confidence,
                2
            ),

        "leafDistribution":
            cnn_leaf,

        "leafDistributionConfidence":
            round(
                cnn_leaf_confidence,
                2
            ),

        "branchDevelopment":
            cnn_branch,

        "branchDevelopmentConfidence":
            round(
                cnn_branch_confidence,
                2
            ),


        # Independent CNN values

        "cnnGrowth":
            cnn_growth,

        "cnnLeafDistribution":
            cnn_leaf,

        "cnnBranchDevelopment":
            cnn_branch

    }


    # ========================================================
    # PRINT CNN RESULT
    # ========================================================

    print("\n============================================")
    print("CNN IMAGE ANALYSIS")
    print("============================================")


    print(

        "Growth:",

        cnn_growth,

        f"({cnn_growth_confidence:.2f}%)"

    )


    print(

        "Leaves:",

        cnn_leaf,

        f"({cnn_leaf_confidence:.2f}%)"

    )


    print(

        "Branches:",

        cnn_branch,

        f"({cnn_branch_confidence:.2f}%)"

    )


    return result


# ============================================================
# 13. MAIN PREDICTION ROUTE
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)

def predict():

    print("\n============================================")
    print("MORPHOGNOSIS PREDICTION REQUEST")
    print("============================================")


    try:

        # ====================================================
        # A. NUMERICAL INPUTS
        # ====================================================

        sunlight = float(
            request.form.get(
                "sunlight"
            )
        )


        temperature = float(
            request.form.get(
                "temperature"
            )
        )


        water = float(
            request.form.get(
                "water"
            )
        )


        week = int(
            request.form.get(
                "week"
            )
        )


        prevHeight = float(
            request.form.get(
                "prevHeight"
            )
        )


        prevLeaves = int(
            request.form.get(
                "prevLeaves"
            )
        )


        prevBranches = int(
            request.form.get(
                "prevBranches"
            )
        )


        print("\nNUMERICAL INPUTS")


        print(
            "Sunlight:",
            sunlight
        )


        print(
            "Temperature:",
            temperature
        )


        print(
            "Water:",
            water
        )


        print(
            "Week:",
            week
        )


        print(
            "Previous Height:",
            prevHeight
        )


        print(
            "Previous Leaves:",
            prevLeaves
        )


        print(
            "Previous Branches:",
            prevBranches
        )


        # ====================================================
        # B. HYBRID FORMULA
        # ====================================================

        hybrid_result = formula.predict(

            sunlight=sunlight,

            temperature=temperature,

            water=water,

            prev_height=prevHeight,

            prev_leaves=prevLeaves,

            prev_branches=prevBranches

        )


        print("\nHYBRID FORMULA RESULT")

        print(
            hybrid_result
        )


        # ====================================================
        # C. XGBOOST
        # ====================================================

        xgb_result = predict_growth(

            sunlight=sunlight,

            temperature=temperature,

            water=water,

            week=week

        )


        print("\nXGBOOST RESULT")

        print(
            xgb_result
        )


        # ====================================================
        # D. COMBINE HYBRID FORMULA + XGBOOST
        # ====================================================

        final_height = (

            hybrid_result["height"]

            +

            xgb_result["height"]

        ) / 2


        final_leaves = (

            hybrid_result["leaves"]

            +

            xgb_result["leaves"]

        ) / 2


        final_branches = (

            hybrid_result["branches"]

            +

            xgb_result["branches"]

        ) / 2


        # ====================================================
        # E. ROUND OUTPUT
        # ====================================================

        predicted_height = round(

            final_height,

            2

        )


        predicted_leaves = round(

            final_leaves

        )


        predicted_branches = round(

            final_branches

        )


        # ====================================================
        # F. NUMERICAL CLASSIFICATION
        # ====================================================

        (

            structural_growth,

            structural_leaf,

            structural_branch

        ) = classify_growth(

            predicted_height,

            predicted_leaves,

            predicted_branches

        )


        # ====================================================
        # G. INITIAL RESULT
        # ====================================================

        final_result = {

            # Numerical prediction

            "predictedHeight":
                predicted_height,

            "predictedLeaves":
                predicted_leaves,

            "predictedBranches":
                predicted_branches,


            # Numerical classification

            "structuralGrowth":
                structural_growth,

            "structuralLeafDistribution":
                structural_leaf,

            "structuralBranchDevelopment":
                structural_branch

        }


        # ====================================================
        # H. PRINT NUMERICAL ANALYSIS
        # ====================================================

        print("\n============================================")
        print("NUMERICAL STRUCTURAL ANALYSIS")
        print("============================================")


        print(

            "Predicted Height:",

            predicted_height,

            "cm"

        )


        print(

            "Predicted Leaves:",

            predicted_leaves

        )


        print(

            "Predicted Branches:",

            predicted_branches

        )


        print(

            "Growth:",

            structural_growth

        )


        print(

            "Leaf Distribution:",

            structural_leaf

        )


        print(

            "Branch Development:",

            structural_branch

        )


        # ====================================================
        # I. GET PLANT IMAGE
        # ====================================================

        image = request.files.get(
            "plantImage"
        )


        if image and image.filename:


            print("\n============================================")
            print("PLANT IMAGE RECEIVED")
            print("============================================")


            # ------------------------------------------------
            # SECURE FILENAME
            # ------------------------------------------------

            filename = secure_filename(
                image.filename
            )


            if not filename:

                raise ValueError(
                    "Invalid image filename."
                )


            print(
                "Filename:",
                filename
            )


            # ------------------------------------------------
            # UPLOAD FOLDER
            # ------------------------------------------------

            upload_folder = os.path.join(

                BASE_DIR,

                "static",

                "uploads"

            )


            os.makedirs(

                upload_folder,

                exist_ok=True

            )


            # ------------------------------------------------
            # IMAGE PATH
            # ------------------------------------------------

            image_path = os.path.join(

                upload_folder,

                filename

            )


            # ------------------------------------------------
            # SAVE IMAGE
            # ------------------------------------------------

            image.save(
                image_path
            )


            print(
                "Image saved:",
                image_path
            )


            # =================================================
            # J. INDEPENDENT CNN ANALYSIS
            # =================================================

            cnn_result = predict_plant_image(

                image_path

            )


            # =================================================
            # K. COMBINE NUMERICAL + CNN
            # =================================================

            combined_result = combine_analysis(

                numerical_growth=
                    structural_growth,

                numerical_leaf=
                    structural_leaf,

                numerical_branch=
                    structural_branch,


                cnn_growth=
                    cnn_result[
                        "cnnGrowth"
                    ],

                cnn_leaf=
                    cnn_result[
                        "cnnLeafDistribution"
                    ],

                cnn_branch=
                    cnn_result[
                        "cnnBranchDevelopment"
                    ],


                cnn_growth_confidence=
                    cnn_result[
                        "overallGrowthConfidence"
                    ],

                cnn_leaf_confidence=
                    cnn_result[
                        "leafDistributionConfidence"
                    ],

                cnn_branch_confidence=
                    cnn_result[
                        "branchDevelopmentConfidence"
                    ]

            )


            # =================================================
            # L. ADD CNN RESULT
            # =================================================

            final_result.update({

                # ---------------------------------------------
                # CNN RESULT
                # ---------------------------------------------

                "cnnGrowth":
                    cnn_result[
                        "cnnGrowth"
                    ],

                "cnnGrowthConfidence":
                    cnn_result[
                        "overallGrowthConfidence"
                    ],


                "cnnLeafDistribution":
                    cnn_result[
                        "cnnLeafDistribution"
                    ],

                "cnnLeafDistributionConfidence":
                    cnn_result[
                        "leafDistributionConfidence"
                    ],


                "cnnBranchDevelopment":
                    cnn_result[
                        "cnnBranchDevelopment"
                    ],

                "cnnBranchDevelopmentConfidence":
                    cnn_result[
                        "branchDevelopmentConfidence"
                    ],


                # ---------------------------------------------
                # COMBINED RESULT
                # ---------------------------------------------

                "finalGrowth":
                    combined_result[
                        "growth"
                    ],

                "finalLeafDistribution":
                    combined_result[
                        "leaf"
                    ],

                "finalBranchDevelopment":
                    combined_result[
                        "branch"
                    ],


                # ---------------------------------------------
                # DOMINANCE
                # ---------------------------------------------

                "growthSource":
                    combined_result[
                        "growthSource"
                    ],

                "leafSource":
                    combined_result[
                        "leafSource"
                    ],

                "branchSource":
                    combined_result[
                        "branchSource"
                    ],


                # ---------------------------------------------
                # IMAGE
                # ---------------------------------------------

                "image":
                    "/static/uploads/"
                    + filename

            })


        else:


            print(
                "\nNo plant image uploaded."
            )


            final_result.update({

                "cnnGrowth":
                    "No image",

                "cnnGrowthConfidence":
                    0,


                "cnnLeafDistribution":
                    "No image",

                "cnnLeafDistributionConfidence":
                    0,


                "cnnBranchDevelopment":
                    "No image",

                "cnnBranchDevelopmentConfidence":
                    0,


                # Without CNN, numerical classification
                # becomes the final result.

                "finalGrowth":
                    structural_growth,

                "finalLeafDistribution":
                    structural_leaf,

                "finalBranchDevelopment":
                    structural_branch,


                "growthSource":
                    "numerical_only",

                "leafSource":
                    "numerical_only",

                "branchSource":
                    "numerical_only"

            })


        # ====================================================
        # M. FINAL TERMINAL OUTPUT
        # ====================================================

        print("\n============================================")
        print("FINAL MORPHOGNOSIS RESULT")
        print("============================================")


        print("\nNUMERICAL MODEL")


        print(

            "Height:",

            final_result[
                "predictedHeight"
            ],

            "cm"

        )


        print(

            "Leaves:",

            final_result[
                "predictedLeaves"
            ]

        )


        print(

            "Branches:",

            final_result[
                "predictedBranches"
            ]

        )


        print("\nSTRUCTURAL CLASSIFICATION")


        print(

            "Growth:",

            final_result[
                "structuralGrowth"
            ]

        )


        print(

            "Leaf Distribution:",

            final_result[
                "structuralLeafDistribution"
            ]

        )


        print(

            "Branch Development:",

            final_result[
                "structuralBranchDevelopment"
            ]

        )


        print("\nCNN IMAGE ANALYSIS")


        print(

            "Growth:",

            final_result.get(
                "cnnGrowth"
            )

        )


        print(

            "Leaf Distribution:",

            final_result.get(
                "cnnLeafDistribution"
            )

        )


        print(

            "Branch Development:",

            final_result.get(
                "cnnBranchDevelopment"
            )

        )


        print("\n============================================")
        print("COMBINED ANALYSIS")
        print("============================================")


        print(

            "Overall Growth:",

            final_result.get(
                "finalGrowth"
            )

        )


        print(

            "Leaf Distribution:",

            final_result.get(
                "finalLeafDistribution"
            )

        )


        print(

            "Branch Development:",

            final_result.get(
                "finalBranchDevelopment"
            )

        )


        print("\nMODEL DOMINANCE")


        print(

            "Growth:",

            final_result.get(
                "growthSource"
            )

        )


        print(

            "Leaves:",

            final_result.get(
                "leafSource"
            )

        )


        print(

            "Branches:",

            final_result.get(
                "branchSource"
            )

        )


        print("\n============================================")
        print("ANALYSIS COMPLETED")
        print("============================================")


        return jsonify(
            final_result
        )


    except Exception as e:


        print("\n============================================")
        print("PREDICTION ERROR")
        print("============================================")


        print(
            str(e)
        )


        return jsonify({

            "error":
                str(e)

        }), 500


# ============================================================
# 14. DIRECT CNN IMAGE ANALYSIS
# ============================================================

@app.route(
    "/analyze_image",
    methods=["POST"]
)

def analyze_image():


    print("\n============================================")
    print("DIRECT CNN IMAGE ANALYSIS")
    print("============================================")


    if "plantImage" not in request.files:

        return jsonify({

            "error":
                "No plant image uploaded."

        }), 400


    image = request.files[
        "plantImage"
    ]


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


    upload_folder = os.path.join(

        BASE_DIR,

        "static",

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


    try:


        results = predict_plant_image(

            image_path

        )


        results["image"] = (

            "/static/uploads/"
            + filename

        )


        return jsonify(
            results
        )


    except Exception as e:


        print(
            "\nCNN ERROR:"
        )


        print(
            str(e)
        )


        return jsonify({

            "error":
                str(e)

        }), 500


# ============================================================
# 15. START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
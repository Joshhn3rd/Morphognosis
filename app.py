from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from models.hybrid_formula import HybridFormula
from models.predict_xgboost import predict_growth

import os
import requests


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
# 3. CNN SERVICE
# ============================================================

# Local default: separate CNN Flask app on port 5001.
# In deployment, set CNN_SERVICE_URL to the public CNN service URL.
CNN_SERVICE_URL = os.getenv(
    "CNN_SERVICE_URL",
    "http://127.0.0.1:5001"
).rstrip("/")


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
        # I. GET PLANT IMAGE + CALL SEPARATE CNN SERVICE
        # ====================================================

        image = request.files.get("plantImage")

        if image and image.filename:

            filename = secure_filename(image.filename)

            if not filename:
                raise ValueError("Invalid image filename.")

            print("\n============================================")
            print("PLANT IMAGE RECEIVED")
            print("============================================")
            print("Filename:", filename)
            print("CNN service:", CNN_SERVICE_URL)

            # Forward the uploaded image to the independent CNN API.
            # The main app never imports TensorFlow or loads MobileNetV2.
            image.stream.seek(0)

            try:
                cnn_response = requests.post(
                    f"{CNN_SERVICE_URL}/analyze_image",
                    files={
                        "plantImage": (
                            filename,
                            image.stream,
                            image.mimetype or "application/octet-stream"
                        )
                    },
                    timeout=60
                )
            except requests.RequestException as exc:
                raise RuntimeError(
                    f"Could not reach CNN service at {CNN_SERVICE_URL}: {exc}"
                ) from exc

            try:
                cnn_result = cnn_response.json()
            except ValueError as exc:
                raise RuntimeError(
                    "CNN service returned a non-JSON response."
                ) from exc

            if not cnn_response.ok:
                raise RuntimeError(
                    cnn_result.get("error")
                    or f"CNN service failed with HTTP {cnn_response.status_code}."
                )

            combined_result = combine_analysis(
                numerical_growth=structural_growth,
                numerical_leaf=structural_leaf,
                numerical_branch=structural_branch,
                cnn_growth=cnn_result["overallGrowth"],
                cnn_leaf=cnn_result["leafDistribution"],
                cnn_branch=cnn_result["branchDevelopment"],
                cnn_growth_confidence=cnn_result["overallGrowthConfidence"],
                cnn_leaf_confidence=cnn_result["leafDistributionConfidence"],
                cnn_branch_confidence=cnn_result["branchDevelopmentConfidence"]
            )

            final_result.update({
                "cnnGrowth": cnn_result["overallGrowth"],
                "cnnGrowthConfidence": cnn_result["overallGrowthConfidence"],
                "cnnLeafDistribution": cnn_result["leafDistribution"],
                "cnnLeafDistributionConfidence": cnn_result["leafDistributionConfidence"],
                "cnnBranchDevelopment": cnn_result["branchDevelopment"],
                "cnnBranchDevelopmentConfidence": cnn_result["branchDevelopmentConfidence"],
                "finalGrowth": combined_result["growth"],
                "finalLeafDistribution": combined_result["leaf"],
                "finalBranchDevelopment": combined_result["branch"],
                "growthSource": combined_result["growthSource"],
                "leafSource": combined_result["leafSource"],
                "branchSource": combined_result["branchSource"],
                "imageFilename": filename
            })

        else:

            print("\nNo plant image uploaded.")

            final_result.update({
                "cnnGrowth": "No image",
                "cnnGrowthConfidence": 0,
                "cnnLeafDistribution": "No image",
                "cnnLeafDistributionConfidence": 0,
                "cnnBranchDevelopment": "No image",
                "cnnBranchDevelopmentConfidence": 0,
                "finalGrowth": structural_growth,
                "finalLeafDistribution": structural_leaf,
                "finalBranchDevelopment": structural_branch,
                "growthSource": "numerical_only",
                "leafSource": "numerical_only",
                "branchSource": "numerical_only"
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
# 15. START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
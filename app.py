from datetime import timedelta

from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename

from models.hybrid_formula import HybridFormula
from models.predict_xgboost import predict_growth

import db as database
from tracker import tracker_bp

import os
import requests


app = Flask(__name__)


# ============================================================
# 0. LOGIN SESSIONS + TRACKER (accounts, stages, daily logger)
# ============================================================

# SECRET_KEY signs the login cookie. Set a long random value in the
# Vercel environment variables. The fallback below is for your own
# computer only, so the site refuses to start on Vercel without one.
_secret_key = os.getenv("SECRET_KEY")

if not _secret_key:
    if database.ON_VERCEL:
        raise RuntimeError(
            "SECRET_KEY is not set. Add it to the Vercel environment variables."
        )
    _secret_key = "local-development-only-change-me"

app.config.update(
    SECRET_KEY=_secret_key,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=database.ON_VERCEL,
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
)

app.register_blueprint(tracker_bp)
app.teardown_appcontext(database.close_db)


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

    # The coefficients shown in "How the prediction is made" are read
    # from the formula itself, so the page can never drift from the code.
    model_rows = [
        {
            "symbol": "H",
            "name": "Height",
            "bias": formula.height_bias,
            "alpha": formula.height_water_weight,
            "beta": formula.height_temperature_weight,
            "gamma": formula.height_sunlight_weight,
            "scale": formula.height_scale,
            "note": "cm gained per week"
        },
        {
            "symbol": "L",
            "name": "Leaves",
            "bias": formula.leaf_bias,
            "alpha": formula.leaf_water_weight,
            "beta": formula.leaf_temperature_weight,
            "gamma": formula.leaf_sunlight_weight,
            "scale": formula.leaf_scale,
            "note": "leaves gained per week (at least 1)"
        },
        {
            "symbol": "B",
            "name": "Branches",
            "bias": formula.branch_bias,
            "alpha": formula.branch_water_weight,
            "beta": formula.branch_temperature_weight,
            "gamma": formula.branch_sunlight_weight,
            "scale": formula.branch_scale,
            "note": (
                "branches gained per week, only once the plant is at "
                f"least {formula.branch_height_threshold:g} cm tall"
            )
        }
    ]

    return render_template(
        "prediction.xhtml",
        model_rows=model_rows,
        ref_sunlight=formula.ref_sunlight,
        ref_temperature=formula.ref_temperature,
        ref_water=formula.ref_water
    )


# ============================================================
# 8. ENVIRONMENT PAGE
# ============================================================

@app.route("/environment")
def environment():

    # Environmental Factors now lives on Home (#environment) and on
    # the /environment/<sunlight|temperature|water> pages.
    return redirect("/#environment", code=301)


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
# 12. THREE-VIEW IMAGE ANALYSIS (TOP, FRONT, SIDE)
# ============================================================
#
# The farmer uploads three photos of the same plant. Each photo is sent
# to the CNN service on its own, then the three answers are combined:
# for every category (growth, leaf distribution, branch development)
# the confidences of the views that chose the same label are added up,
# and the label with the highest total wins.
#
# VIEW_WEIGHTS lets you trust one view more than another for a category.
# All are 1.0 (equal) because no per-view accuracy has been measured yet.

PLANT_VIEWS = [
    ("top", "plantImageTop"),
    ("front", "plantImageFront"),
    ("side", "plantImageSide"),
]

VIEW_WEIGHTS = {
    "growth": {"top": 1.0, "front": 1.0, "side": 1.0},
    "leaf": {"top": 1.0, "front": 1.0, "side": 1.0},
    "branch": {"top": 1.0, "front": 1.0, "side": 1.0},
}


def collect_plant_views(files):

    views = []

    for view_name, field in PLANT_VIEWS:

        image = files.get(field)

        if image and image.filename:
            views.append((view_name, image))

    if not views:

        legacy = files.get("plantImage")

        if legacy and legacy.filename:
            views.append(("single", legacy))

    return views


def analyze_view(view_name, image):

    filename = secure_filename(image.filename)

    if not filename:
        raise ValueError(f"Invalid image filename ({view_name} view).")

    image.stream.seek(0)

    try:
        response = requests.post(
            f"{CNN_SERVICE_URL}/analyze_image",
            files={
                "plantImage": (
                    filename,
                    image.stream,
                    image.mimetype or "application/octet-stream"
                )
            },
            timeout=180
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach CNN service at {CNN_SERVICE_URL}: {exc}"
        ) from exc

    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "CNN service returned a non-JSON response."
        ) from exc

    if not response.ok:
        raise RuntimeError(
            result.get("error")
            or f"CNN service failed with HTTP {response.status_code} "
               f"({view_name} view)."
        )

    result["view"] = view_name

    return result


def aggregate_views(view_results):

    categories = [
        ("growth", "overallGrowth", "overallGrowthConfidence"),
        ("leaf", "leafDistribution", "leafDistributionConfidence"),
        ("branch", "branchDevelopment", "branchDevelopmentConfidence"),
    ]

    combined = {}
    agree = True

    for key, label_field, conf_field in categories:

        totals = {}
        weight_sum = 0.0

        for r in view_results:

            weight = VIEW_WEIGHTS[key].get(r["view"], 1.0)
            label = str(r[label_field]).lower()

            totals[label] = (
                totals.get(label, 0.0)
                + weight * float(r[conf_field])
            )

            weight_sum += weight

        winner = max(totals, key=totals.get)

        combined[label_field] = winner
        combined[conf_field] = round(totals[winner] / weight_sum, 2)

        if len(totals) > 1:
            agree = False

    combined["viewsAgree"] = agree

    return combined


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

        # Three required views (top, front, side). A single legacy
        # "plantImage" upload is still accepted.
        views = collect_plant_views(request.files)

        if views:

            print("\n============================================")
            print("PLANT IMAGES RECEIVED:", [v[0] for v in views])
            print("CNN service:", CNN_SERVICE_URL)

            view_results = []

            for view_name, image in views:
                view_results.append(
                    analyze_view(view_name, image)
                )

            cnn_result = aggregate_views(view_results)

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
                "viewResults": view_results,
                "viewsAgree": cnn_result["viewsAgree"]
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
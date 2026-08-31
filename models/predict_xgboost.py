import pickle
import numpy as np
import os

print("Loading XGBoost models...")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "saved_models")

with open(os.path.join(MODEL_PATH, "xgb_height.pkl"), "rb") as file:
    height_model = pickle.load(file)

with open(os.path.join(MODEL_PATH, "xgb_leaves.pkl"), "rb") as file:
    leaves_model = pickle.load(file)

with open(os.path.join(MODEL_PATH, "xgb_branches.pkl"), "rb") as file:
    branches_model = pickle.load(file)

print("Models loaded successfully.")


def predict_growth(sunlight, temperature, water, week):

    print("predict_growth() called")

    input_data = np.array([[
        sunlight,
        temperature,
        water,
        week
    ]])

    print(input_data)

    height = height_model.predict(input_data)[0]
    leaves = leaves_model.predict(input_data)[0]
    branches = branches_model.predict(input_data)[0]

    print(height, leaves, branches)

    return {
        "height": float(height),
        "leaves": float(leaves),
        "branches": float(branches)
    }
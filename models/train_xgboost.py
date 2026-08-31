import os
import pandas as pd
import xgboost as xgb
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np


# Get main project folder
base_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# Dataset location
dataset_path = os.path.join(
    base_path,
    "dataset",
    "weekly_growth.csv"
)


# Load dataset
data = pd.read_csv(dataset_path)


print("Dataset loaded successfully")
print(data.head())


# Input features
X = data[
    [
        "sunlight",
        "temperature",
        "water",
        "week"
    ]
]


# Target variables
targets = {
    "height": data["height"],
    "leaves": data["leaves"],
    "branches": data["branches"]
}


# Train each XGBoost model
for name, y in targets.items():

    print("\nTraining model:", name)


    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )


    # Create XGBoost model
    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )


    # Train model
    model.fit(
        X_train,
        y_train
    )


    # Predict
    prediction = model.predict(X_test)


    # Evaluate
    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            prediction
        )
    )

    r2 = r2_score(
        y_test,
        prediction
    )


    print("RMSE:", rmse)
    print("R²:", r2)


    # Save trained model
    model_path = os.path.join(
        base_path,
        "saved_models",
        f"xgb_{name}.pkl"
    )


    with open(model_path, "wb") as file:
        pickle.dump(
            model,
            file
        )


    print("Saved:", model_path)


print("\nAll models trained successfully.")
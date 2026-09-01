from models.hybrid_formula import HybridFormula
from models.lsystem import LSystem
from models.fspm import FSPM


# -----------------------------
# Sample Inputs
# -----------------------------

sunlight = 7.5
temperature = 28
water = 350

prev_height = 1.9
prev_leaves = 2
prev_branches = 0


# -----------------------------
# Hybrid Formula
# -----------------------------

formula = HybridFormula()

prediction = formula.predict(
    sunlight,
    temperature,
    water,
    prev_height,
    prev_leaves,
    prev_branches
)

print("\n===== HYBRID FORMULA =====")
print(prediction)


# -----------------------------
# L-System
# -----------------------------

lsystem = LSystem(
    prediction["height"],
    prediction["leaves"],
    prediction["branches"]
)

plant = lsystem.generate_structure()

print("\n===== L-SYSTEM =====")
print(plant)


# -----------------------------
# FSPM
# -----------------------------

fspm = FSPM(plant)

plant = fspm.simulate()

print("\n===== FSPM =====")
print(plant)


# -----------------------------
# Draw Plant
# -----------------------------

print("\nDrawing Plant...")

lsystem.draw_structure(plant)

print("\nPipeline Test Successful!")
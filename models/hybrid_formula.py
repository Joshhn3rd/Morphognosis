"""
Morphognosis Hybrid Formula

Phase 3
Predicts:
- Plant Height
- Number of Leaves
- Number of Branches
"""

class HybridFormula:

    def __init__(self):

        # ---------------------------------
        # Reference Values (Normalization)
        # ---------------------------------

        self.ref_sunlight = 8.0        # hours/day
        self.ref_temperature = 30.0    # °C
        self.ref_water = 1000.0        # mL/week

        # ==========================================
        # HEIGHT PARAMETERS
        # ==========================================

        self.height_bias = 0.10

        self.height_water_weight = 0.40
        self.height_temperature_weight = 0.25
        self.height_sunlight_weight = 0.35

        self.height_scale = 1.50

        # ==========================================
        # LEAF PARAMETERS
        # ==========================================

        self.leaf_bias = 0.05

        self.leaf_water_weight = 0.30
        self.leaf_temperature_weight = 0.20
        self.leaf_sunlight_weight = 0.50

        self.leaf_scale = 1.00

        # ==========================================
        # BRANCH PARAMETERS
        # ==========================================

        self.branch_bias = 0.00

        self.branch_water_weight = 0.25
        self.branch_temperature_weight = 0.25
        self.branch_sunlight_weight = 0.50

        self.branch_scale = 0.50

        self.branch_height_threshold = 8.0


    def predict(

        self,

        sunlight,
        temperature,
        water,

        prev_height,
        prev_leaves,
        prev_branches

    ):

        # ---------------------------------
        # Normalize Environmental Inputs
        # ---------------------------------

        sunlight = sunlight / self.ref_sunlight
        temperature = temperature / self.ref_temperature
        water = water / self.ref_water


        # ==========================================
        # HEIGHT GROWTH SCORE
        # ==========================================

        height_score = (

            self.height_bias +

            (water * self.height_water_weight) +

            (temperature * self.height_temperature_weight) +

            (sunlight * self.height_sunlight_weight)

        )

        predicted_height = (

            prev_height +

            (height_score * self.height_scale)

        )


        # ==========================================
        # LEAF GROWTH SCORE
        # ==========================================

        leaf_score = (

            self.leaf_bias +

            (water * self.leaf_water_weight) +

            (temperature * self.leaf_temperature_weight) +

            (sunlight * self.leaf_sunlight_weight)

        )

        predicted_leaves = (

            prev_leaves +

            max(1, round(leaf_score * self.leaf_scale))

        )


        # ==========================================
        # BRANCH GROWTH SCORE
        # ==========================================

        branch_score = (

            self.branch_bias +

            (water * self.branch_water_weight) +

            (temperature * self.branch_temperature_weight) +

            (sunlight * self.branch_sunlight_weight)

        )

        if predicted_height >= self.branch_height_threshold:

            predicted_branches = (

                prev_branches +

                max(1, round(branch_score * self.branch_scale))

            )

        else:

            predicted_branches = prev_branches


        # ==========================================
        # RETURN
        # ==========================================

        return {

            "height": round(predicted_height, 2),

            "leaves": predicted_leaves,

            "branches": predicted_branches,

            "height_score": round(height_score, 3),

            "leaf_score": round(leaf_score, 3),

            "branch_score": round(branch_score, 3)

        }


# ==========================================
# Example
# ==========================================

if __name__ == "__main__":

    formula = HybridFormula()

    result = formula.predict(

        sunlight=7,
        temperature=28,
        water=840,

        prev_height=1.2,
        prev_leaves=2,
        prev_branches=0

    )

    print(result)
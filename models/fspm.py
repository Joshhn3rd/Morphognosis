"""
Morphognosis
Functional-Structural Plant Model (FSPM)

Purpose:
Acts as the functional layer between the
L-System and the CNN. It prepares the
generated plant structure for visualization
and future CNN validation.

Version: 1.0
"""


class FSPM:

    def __init__(self, plant):

        self.plant = plant

    def simulate(self):

        """
        Prepare the generated plant structure
        for visualization and CNN validation.
        """

        self.add_growth_stage()

        self.add_metadata()

        return self.plant

    def add_growth_stage(self):

        """
        Assign a simple growth stage
        based on predicted plant height.
        """

        stem = self.plant["stem"]

        if stem["length"] < 10:

            stage = "Seedling"

        elif stem["length"] < 30:

            stage = "Vegetative"

        else:

            stage = "Mature"

        self.plant["growth_stage"] = stage

    def add_metadata(self):

        """
        Store basic information that can be
        used by the website and future modules.
        """

        self.plant["model"] = "Morphognosis"

        self.plant["structure_type"] = "2D"

        self.plant["status"] = "Predicted"
"""
Morphognosis
L-System Module

Purpose:
Generate a simple 2D eggplant structure based on
predicted plant height, leaves, and branches.

Version: 1.0
"""

import matplotlib.pyplot as plt


class LSystem:

    def __init__(self, height, leaves, branches):

        self.height = height
        self.leaves = leaves
        self.branches = branches

    def generate_structure(self):

        plant = {
            "stem": self.create_stem(),
            "branches": self.create_branches(),
            "leaves": self.create_leaves()
        }

        return plant

    def create_stem(self):

        stem = {
            "length": self.height,
            "nodes": max(1, self.leaves // 2)
        }

        return stem

    def create_branches(self):

        branch_list = []

        for i in range(self.branches):

            side = "left" if i % 2 == 0 else "right"

            branch = {
                "id": i + 1,
                "side": side,
                "length": round(self.height * 0.30, 2)
            }

            branch_list.append(branch)

        return branch_list

    def create_leaves(self):

        leaf_list = []

        if self.leaves == 0:
            return leaf_list

        spacing = self.height / self.leaves

        for i in range(self.leaves):

            leaf = {
                "id": i + 1,
                "position": round((i + 1) * spacing, 2)
            }

            leaf_list.append(leaf)

        return leaf_list

    def draw_structure(self, structure):

        plt.figure(figsize=(6, 8))

        # Draw the main stem
        stem_length = structure["stem"]["length"]

        plt.plot(
            [0, 0],
            [0, stem_length],
            linewidth=4,
            color="green"
        )

        # Draw branches
        if len(structure["branches"]) > 0:

            branch_spacing = stem_length / (len(structure["branches"]) + 1)

            for i, branch in enumerate(structure["branches"]):

                y = branch_spacing * (i + 1)

                if branch["side"] == "left":
                    x2 = -2
                else:
                    x2 = 2

                y2 = y + branch["length"] * 0.6

                plt.plot(
                    [0, x2],
                    [y, y2],
                    linewidth=2,
                    color="brown"
                )

        # Draw leaves
        for leaf in structure["leaves"]:

            y = leaf["position"]

            plt.scatter(
                -0.3,
                y,
                s=40,
                color="green"
            )

            plt.scatter(
                0.3,
                y,
                s=40,
                color="green"
            )

        # Display growth stage if available
        if "growth_stage" in structure:

            plt.title(
                f"Morphognosis - {structure['growth_stage']} Eggplant"
            )

        else:

            plt.title(
                "Morphognosis - L-System Eggplant Skeleton"
            )

        plt.axis("equal")
        plt.axis("off")

        plt.show()
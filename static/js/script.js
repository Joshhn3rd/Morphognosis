const imageInput = document.getElementById("plantImage");
const imagePreview = document.getElementById("preview");
const predictionForm = document.getElementById("predictionForm");


// ============================================================
// IMAGE PREVIEW
// ============================================================

if (imageInput && imagePreview) {

    imageInput.addEventListener("change", () => {

        const file = imageInput.files[0];

        if (!file) {
            return;
        }

        if (!file.type.startsWith("image/")) {

            alert("Please select a valid image file.");

            imageInput.value = "";

            return;
        }

        const reader = new FileReader();

        reader.onload = (event) => {

            imagePreview.src = event.target.result;
            imagePreview.style.display = "block";

        };

        reader.readAsDataURL(file);

    });

}


// ============================================================
// NUMERICAL + FINAL PLANT ANALYSIS
// ============================================================

async function predictStructure() {

    const formData = new FormData(predictionForm);

    const response = await fetch(
        "/predict",
        {
            method: "POST",
            body: formData
        }
    );

    const result = await response.json();

    if (!response.ok || result.error) {

        throw new Error(
            result.error ||
            "Plant prediction failed."
        );

    }

    return result;

}


// ============================================================
// PREDICTION FORM
// ============================================================

if (predictionForm) {

    predictionForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            // ====================================================
            // CHECK IMAGE
            // ====================================================

            if (
                !imageInput ||
                !imageInput.files[0]
            ) {

                alert(
                    "Please upload a plant image."
                );

                return;

            }


            // ====================================================
            // SHOW PROCESSING
            // ====================================================

            setResult(
                "predictedHeight",
                "Processing..."
            );

            setResult(
                "predictedLeaves",
                "Processing..."
            );

            setResult(
                "predictedBranches",
                "Processing..."
            );

            setResult(
                "cnnGrowth",
                "Analyzing..."
            );

            setResult(
                "cnnLeafDistribution",
                "Analyzing..."
            );

            setResult(
                "cnnBranchDevelopment",
                "Analyzing..."
            );


            try {


                // ====================================================
                // 1. SEND EVERYTHING TO BACKEND
                // ====================================================
                //
                // The backend performs:
                //
                // Hybrid Formula
                // +
                // XGBoost
                // +
                // CNN image analysis
                // +
                // final combination
                //
                // The frontend does NOT perform the combination.
                // ====================================================

                const result =
                    await predictStructure();


                console.log(
                    "MORPHOGNOSIS FINAL RESULT:",
                    result
                );


                // ====================================================
                // 2. DISPLAY NUMERICAL PREDICTION
                // ====================================================

                setResult(
                    "predictedHeight",
                    `${result.predictedHeight} cm`
                );

                setResult(
                    "predictedLeaves",
                    result.predictedLeaves
                );

                setResult(
                    "predictedBranches",
                    result.predictedBranches
                );


                // ====================================================
                // 3. DISPLAY FINAL PLANT ANALYSIS
                // ====================================================
                //
                // IMPORTANT:
                //
                // These are the COMBINED results from the backend.
                //
                // The user does not see whether the result came
                // from numerical analysis, CNN, or both.
                // ====================================================

                setResult(
                    "cnnGrowth",
                    result.finalGrowth || "No result"
                );

                setResult(
                    "cnnLeafDistribution",
                    result.finalLeafDistribution || "No result"
                );

                setResult(
                    "cnnBranchDevelopment",
                    result.finalBranchDevelopment || "No result"
                );


                // ====================================================
                // 4. SAVE FINAL RESULT TO HISTORY
                // ====================================================

                saveHistory(
                    result
                );


                console.log(
                    "============================================"
                );

                console.log(
                    "MORPHOGNOSIS ANALYSIS COMPLETED"
                );

                console.log(
                    "============================================"
                );


            }

            catch (error) {

                console.error(
                    "Morphognosis error:",
                    error
                );


                // ====================================================
                // NUMERICAL ERROR
                // ====================================================

                setResult(
                    "predictedHeight",
                    "Prediction Failed"
                );

                setResult(
                    "predictedLeaves",
                    "-"
                );

                setResult(
                    "predictedBranches",
                    "-"
                );


                // ====================================================
                // PLANT ANALYSIS ERROR
                // ====================================================

                setResult(
                    "cnnGrowth",
                    "Analysis Failed"
                );

                setResult(
                    "cnnLeafDistribution",
                    "-"
                );

                setResult(
                    "cnnBranchDevelopment",
                    "-"
                );


                alert(
                    error.message
                );

            }

        }
    );

}


// ============================================================
// SET RESULT
// ============================================================

function setResult(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (element) {

        element.textContent = value;

    }

}


// ============================================================
// SAVE PREDICTION HISTORY
// ============================================================

function saveHistory(
    result
) {

    const formData =
        new FormData(
            predictionForm
        );


    const history =
        JSON.parse(
            localStorage.getItem(
                "growthHistory"
            )
        ) || [];


    history.push({

        date:
            new Date().toLocaleString(),


        // ====================================================
        // ENVIRONMENTAL INPUTS
        // ====================================================

        sunlight:
            formData.get("sunlight"),

        temperature:
            formData.get("temperature"),

        water:
            formData.get("water"),

        week:
            formData.get("week"),


        // ====================================================
        // PREVIOUS STRUCTURE
        // ====================================================

        prevHeight:
            formData.get("prevHeight"),

        prevLeaves:
            formData.get("prevLeaves"),

        prevBranches:
            formData.get("prevBranches"),


        // ====================================================
        // NUMERICAL PREDICTION
        // ====================================================

        predictedHeight:
            result.predictedHeight,

        predictedLeaves:
            result.predictedLeaves,

        predictedBranches:
            result.predictedBranches,


        // ====================================================
        // FINAL PLANT ANALYSIS
        // ====================================================
        //
        // These are the combined backend results.
        // ====================================================

        plantGrowth:
            result.finalGrowth || "-",

        leafDistribution:
            result.finalLeafDistribution || "-",

        branchDevelopment:
            result.finalBranchDevelopment || "-"

    });


    localStorage.setItem(
        "growthHistory",
        JSON.stringify(history)
    );


    console.log(
        "Prediction history saved."
    );

}


// ============================================================
// LOAD PREDICTION HISTORY
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const table =
            document.querySelector(
                "#historyTable tbody"
            );


        if (!table) {

            return;

        }


        const history =
            JSON.parse(
                localStorage.getItem(
                    "growthHistory"
                )
            ) || [];


        history.forEach(
            (item) => {

                const row =
                    table.insertRow();


                row.innerHTML = `

                    <td>
                        ${item.date}
                    </td>

                    <td>
                        ${item.sunlight} hrs
                    </td>

                    <td>
                        ${item.temperature} °C
                    </td>

                    <td>
                        ${item.water} mL
                    </td>

                    <td>
                        Height:
                        ${item.prevHeight} cm
                        <br>

                        Leaves:
                        ${item.prevLeaves}
                        <br>

                        Branches:
                        ${item.prevBranches}
                    </td>

                    <td>
                        Height:
                        ${item.predictedHeight} cm
                        <br>

                        Leaves:
                        ${item.predictedLeaves}
                        <br>

                        Branches:
                        ${item.predictedBranches}
                    </td>

                `;

            }
        );

    }
);
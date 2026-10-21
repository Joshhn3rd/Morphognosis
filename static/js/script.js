const predictionForm = document.getElementById("predictionForm");

const VIEW_KEYS = ["Top", "Front", "Side"];


// ============================================================
// IMAGE PREVIEWS (TOP, FRONT, SIDE)
// ============================================================

VIEW_KEYS.forEach((key) => {

    const input = document.getElementById("plantImage" + key);
    const preview = document.getElementById("preview" + key);

    if (!input || !preview) {
        return;
    }

    input.addEventListener("change", () => {

        const file = input.files[0];

        if (!file) {
            preview.hidden = true;
            return;
        }

        if (!file.type.startsWith("image/")) {

            alert("Please select a valid image file.");

            input.value = "";
            preview.hidden = true;

            return;
        }

        const reader = new FileReader();

        reader.onload = (event) => {

            preview.src = event.target.result;
            preview.hidden = false;

        };

        reader.readAsDataURL(file);

    });

});


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
            // CHECK THE THREE PHOTOS
            // ====================================================

            const missing = VIEW_KEYS.filter((key) => {

                const input = document.getElementById(
                    "plantImage" + key
                );

                return !input || !input.files[0];

            });

            if (missing.length) {

                alert(
                    "Please upload all three photos. Missing: " +
                    missing.map((k) => k.toLowerCase() + " view").join(", ") +
                    "."
                );

                return;

            }


            // ====================================================
            // SHOW PROCESSING
            // ====================================================

            if (window.clearGuidance) {
                window.clearGuidance();
            }

            const yours = document.getElementById("modelYours");

            if (yours) {
                yours.hidden = true;
            }

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


                // ====================================================
                // 5. SHOW GUIDANCE FOR THE FARMER
                // ====================================================

                if (window.renderGuidance) {
                    window.renderGuidance(
                        result,
                        new FormData(predictionForm)
                    );
                }


                showModelValues(
                    result,
                    new FormData(predictionForm)
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

                if (window.clearGuidance) {
                    window.clearGuidance();
                }


                alert(
                    error.message
                );

            }

        }
    );

}


// ============================================================
// SHOW THE USER'S OWN NUMBERS IN THE MODEL
// ============================================================

function showModelValues(
    result,
    form
) {

    const box = document.getElementById("modelYours");
    const list = document.getElementById("modelYoursList");

    if (!box || !list) {
        return;
    }

    const week = parseInt(form.get("week"), 10);

    const rows = [
        `n = ${week} (predicting week ${week})`,
        `H\u2099\u208B\u2081 = ${form.get("prevHeight")} cm, ` +
            `L\u2099\u208B\u2081 = ${form.get("prevLeaves")}, ` +
            `B\u2099\u208B\u2081 = ${form.get("prevBranches")}`,
        `W\u2099 = ${form.get("water")} mL, ` +
            `T\u2099 = ${form.get("temperature")} \u00B0C, ` +
            `S\u2099 = ${form.get("sunlight")} hours/day`,
        `H\u2099 = ${result.predictedHeight} cm, ` +
            `L\u2099 = ${result.predictedLeaves}, ` +
            `B\u2099 = ${result.predictedBranches}`
    ];

    list.textContent = "";

    rows.forEach((text) => {
        const li = document.createElement("li");
        li.textContent = text;
        list.appendChild(li);
    });

    box.hidden = false;

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
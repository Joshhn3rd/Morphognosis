/* =========================================================
   MORPHOGNOSIS - stage page
   1. Highlights the recommendation row for today's temperature
   2. Daily measurement logger (week -> day -> save -> weekly averages)
========================================================= */

(function () {
    "use strict";


    /* -----------------------------------------------------
       1. TODAY'S TEMPERATURE -> HIGHLIGHT ROW
    ----------------------------------------------------- */

    var tempInput = document.getElementById("todayTemp");
    var recRows = document.querySelectorAll("#recTable tbody tr");

    if (tempInput && recRows.length) {
        tempInput.addEventListener("input", function () {
            var value = parseFloat(tempInput.value);

            recRows.forEach(function (row) {
                var lo = row.dataset.lo === "" ? -Infinity : parseFloat(row.dataset.lo);
                var hi = row.dataset.hi === "" ? Infinity : parseFloat(row.dataset.hi);
                var match = !isNaN(value) && value >= lo && value < hi;
                row.classList.toggle("rec-active", match);
            });
        });
    }


    /* -----------------------------------------------------
       2. LOGGER
    ----------------------------------------------------- */

    var logger = document.getElementById("logger");

    if (!logger || logger.dataset.signedIn !== "yes") {
        return;
    }

    var slug = logger.dataset.slug;
    var csrf = logger.dataset.csrf;
    var config = JSON.parse(document.getElementById("loggerConfig").textContent);
    var fields = config.fields;

    var weekSelect = document.getElementById("weekSelect");
    var dayButtons = Array.prototype.slice.call(document.querySelectorAll(".day-btn"));
    var form = document.getElementById("logForm");
    var formTitle = document.getElementById("logFormTitle");
    var saveBtn = document.getElementById("saveBtn");
    var saveStatus = document.getElementById("saveStatus");
    var errorBox = document.getElementById("loggerError");
    var summaryBody = document.querySelector("#summaryTable tbody");
    var entriesBody = document.querySelector("#entriesTable tbody");

    var state = {
        entries: [],
        summary: [],
        week: null,
        day: null,
        dirty: false
    };


    /* ---------- small helpers ---------- */

    function cell(text, className) {
        var td = document.createElement("td");
        td.textContent = text;
        if (className) { td.className = className; }
        return td;
    }

    function showError(message, withSignIn) {
        errorBox.textContent = message;
        if (withSignIn) {
            errorBox.appendChild(document.createTextNode(" "));
            var a = document.createElement("a");
            a.href = "/login?next=/stage/" + slug;
            a.textContent = "Sign in again";
            errorBox.appendChild(a);
        }
        errorBox.hidden = false;
    }

    function clearError() {
        errorBox.hidden = true;
        errorBox.textContent = "";
    }

    function setStatus(text, kind) {
        saveStatus.textContent = text;
        saveStatus.className = "save-status" + (kind ? " " + kind : "");
    }

    function entryFor(week, day) {
        for (var i = 0; i < state.entries.length; i++) {
            if (state.entries[i].week === week && state.entries[i].day === day) {
                return state.entries[i];
            }
        }
        return null;
    }

    function confirmDiscard() {
        if (!state.dirty) { return true; }
        return window.confirm("You have unsaved changes. Leave without saving?");
    }

    function request(method, url, body) {
        var options = {
            method: method,
            headers: { "X-CSRF-Token": csrf },
            credentials: "same-origin"
        };
        if (body !== undefined) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }
        return fetch(url, options).then(function (response) {
            return response.json().catch(function () { return {}; })
                .then(function (data) {
                    if (!response.ok) {
                        var err = new Error(data.error || "Something went wrong. Please try again.");
                        err.status = response.status;
                        throw err;
                    }
                    return data;
                });
        });
    }

    function handleFailure(err) {
        if (err.status === 401) {
            showError("Your sign-in expired.", true);
        } else if (err instanceof TypeError) {
            showError("Could not reach the server. Check your connection. Nothing was lost on this page.");
        } else {
            showError(err.message);
        }
    }


    /* ---------- rendering ---------- */

    function fmt(value) {
        return value === null || value === undefined ? "-" : String(value);
    }

    function renderSummary() {
        summaryBody.textContent = "";

        state.summary.forEach(function (week) {
            var tr = document.createElement("tr");
            tr.appendChild(cell("Week " + week.week));
            tr.appendChild(cell(week.daysLogged + " of " + week.daysTotal + " days"));
            fields.forEach(function (f) {
                tr.appendChild(cell(fmt(week.averages[f.key])));
            });
            tr.appendChild(cell(fmt(week.weeklyWaterEstimate)));
            summaryBody.appendChild(tr);
        });
    }

    function renderEntries() {
        entriesBody.textContent = "";

        if (!state.entries.length) {
            var empty = document.createElement("tr");
            var td = cell("No measurements saved yet.", "empty-row");
            td.colSpan = fields.length + 3;
            empty.appendChild(td);
            entriesBody.appendChild(empty);
            return;
        }

        state.entries.forEach(function (entry) {
            var tr = document.createElement("tr");
            tr.appendChild(cell("Week " + entry.week));
            tr.appendChild(cell("Day " + entry.day));
            fields.forEach(function (f) {
                tr.appendChild(cell(fmt(entry[f.key])));
            });

            var actions = document.createElement("td");
            actions.className = "row-actions";

            var edit = document.createElement("button");
            edit.type = "button";
            edit.className = "row-btn";
            edit.textContent = "Edit";
            edit.addEventListener("click", function () {
                selectEntry(entry.week, entry.day);
                form.scrollIntoView({ behavior: "smooth", block: "center" });
            });

            var del = document.createElement("button");
            del.type = "button";
            del.className = "row-btn row-btn-danger";
            del.textContent = "Delete";
            del.addEventListener("click", function () {
                deleteEntry(entry.week, entry.day);
            });

            actions.appendChild(edit);
            actions.appendChild(del);
            tr.appendChild(actions);
            entriesBody.appendChild(tr);
        });
    }

    function renderDayButtons() {
        dayButtons.forEach(function (btn) {
            var day = parseInt(btn.dataset.day, 10);
            var enabled = state.week !== null;
            var logged = enabled && entryFor(state.week, day) !== null;

            btn.disabled = !enabled;
            btn.classList.toggle("day-logged", logged);
            btn.classList.toggle("day-selected", enabled && state.day === day);
            btn.setAttribute("aria-pressed", state.day === day ? "true" : "false");
            btn.title = logged ? "Saved" : "";
        });
    }

    function applyData(data) {
        state.entries = data.entries;
        state.summary = data.summary;
        renderSummary();
        renderEntries();
        renderDayButtons();
    }


    /* ---------- selecting week / day ---------- */

    function fillForm(entry) {
        fields.forEach(function (f) {
            var input = document.getElementById("f_" + f.key);
            input.value = entry ? entry[f.key] : "";
        });
    }

    function selectDay(day) {
        state.day = day;
        var entry = entryFor(state.week, day);
        fillForm(entry);
        formTitle.textContent = "Week " + state.week + ", Day " + day +
            (entry ? " (saved - editing)" : " (new entry)");
        form.hidden = false;
        state.dirty = false;
        setStatus("");
        clearError();
        renderDayButtons();
    }

    function selectEntry(week, day) {
        if (!confirmDiscard()) { return; }
        weekSelect.value = String(week);
        state.week = week;
        selectDay(day);
    }

    weekSelect.addEventListener("change", function () {
        var chosen = weekSelect.value === "" ? null : parseInt(weekSelect.value, 10);

        if (!confirmDiscard()) {
            weekSelect.value = state.week === null ? "" : String(state.week);
            return;
        }

        state.week = chosen;
        state.day = null;
        state.dirty = false;
        form.hidden = true;
        setStatus("");
        clearError();
        renderDayButtons();
    });

    dayButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            var day = parseInt(btn.dataset.day, 10);
            if (day === state.day) { return; }
            if (!confirmDiscard()) { return; }
            selectDay(day);
        });
    });

    form.addEventListener("input", function () {
        state.dirty = true;
        setStatus("Not saved yet", "warn");
    });


    /* ---------- save / delete ---------- */

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        clearError();

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        var payload = {};
        fields.forEach(function (f) {
            payload[f.key] = document.getElementById("f_" + f.key).value;
        });

        saveBtn.disabled = true;
        setStatus("Saving...");

        request("PUT", "/api/logs/" + state.week + "/" + state.day, payload)
            .then(function (data) {
                applyData(data);
                state.dirty = false;
                var entry = entryFor(state.week, state.day);
                formTitle.textContent = "Week " + state.week + ", Day " + state.day +
                    (entry ? " (saved - editing)" : "");
                setStatus("Saved", "ok");
            })
            .catch(function (err) {
                setStatus("Not saved", "error");
                handleFailure(err);
            })
            .then(function () {
                saveBtn.disabled = false;
            });
    });

    function deleteEntry(week, day) {
        var ok = window.confirm(
            "Delete the measurements for Week " + week + ", Day " + day +
            "? This cannot be undone."
        );
        if (!ok) { return; }

        clearError();

        request("DELETE", "/api/logs/" + week + "/" + day)
            .then(function (data) {
                applyData(data);
                if (state.week === week && state.day === day) {
                    selectDay(day);
                }
            })
            .catch(handleFailure);
    }

    window.addEventListener("beforeunload", function (event) {
        if (state.dirty) {
            event.preventDefault();
            event.returnValue = "";
        }
    });


    /* ---------- first load ---------- */

    request("GET", "/api/logs/" + slug)
        .then(applyData)
        .catch(handleFailure);

})();

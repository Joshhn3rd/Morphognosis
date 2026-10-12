/* =========================================================
   MORPHOGNOSIS - Sunlight page stage stepper
   Tabs (Germination / Growing / Fruiting / Ripening) and a
   green arrow that moves to the next stage.
========================================================= */

(function () {
    "use strict";

    var tabs = Array.prototype.slice.call(document.querySelectorAll(".step-tab"));
    var panels = Array.prototype.slice.call(document.querySelectorAll(".step-panel"));
    var next = document.getElementById("stepNext");

    if (!tabs.length) { return; }

    var current = 0;

    function show(index) {
        current = (index + tabs.length) % tabs.length;

        tabs.forEach(function (tab, i) {
            tab.setAttribute("aria-selected", i === current ? "true" : "false");
            tab.tabIndex = i === current ? 0 : -1;
        });

        panels.forEach(function (panel, i) {
            panel.hidden = i !== current;
        });
    }

    tabs.forEach(function (tab, i) {
        tab.addEventListener("click", function () { show(i); });

        tab.addEventListener("keydown", function (event) {
            if (event.key === "ArrowRight") { show(current + 1); tabs[current].focus(); }
            if (event.key === "ArrowLeft") { show(current - 1); tabs[current].focus(); }
        });
    });

    if (next) {
        next.addEventListener("click", function () { show(current + 1); });
    }

    show(0);
})();

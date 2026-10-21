/* =========================================================
   MORPHOGNOSIS - farmer guidance under the prediction results
   Plain, rule-based tips built from:
     - the values the farmer typed in,
     - the predicted structure,
     - the plant analysis (growth / leaves / branches),
     - the DA-RFO 02 Eggplant Production Guide (2017).
   The tips are general guidance, not a diagnosis.
========================================================= */

(function () {
    "use strict";

    var box = document.getElementById("guidanceCard");
    var list = document.getElementById("guidanceList");

    if (!box || !list) { return; }

    function num(value) {
        var n = parseFloat(value);
        return isNaN(n) ? null : n;
    }

    function lower(value) {
        return String(value || "").toLowerCase();
    }

    function stageOf(week) {
        if (week <= 4) { return "seedling"; }
        if (week <= 8) { return "vegetative"; }
        return "mature";
    }

    // tone: "act" (needs attention), "watch" (keep an eye), "ok" (good)
    function tip(tone, title, text) {
        return { tone: tone, title: title, text: text };
    }


    /* ---------- temperature (DA guide + project slides) ---------- */

    function temperatureTip(t) {
        if (t === null) { return null; }

        if (t < 16) {
            return tip("act", "Temperature is too cold (" + t + " °C)",
                "Eggplant grows best at 21-30 °C. Below about 16 °C growth " +
                "slows and flowers and pollen drop. Water lightly because the plant " +
                "uses less water.");
        }
        if (t < 21) {
            return tip("watch", "Temperature is a little cool (" + t + " °C)",
                "Growth may be slower than usual. Keep the soil moist but not soggy.");
        }
        if (t <= 30) {
            return tip("ok", "Temperature is in the best range (" + t + " °C)",
                "21-30 °C is the ideal growing range for eggplant.");
        }
        if (t <= 35) {
            return tip("watch", "Temperature is hot (" + t + " °C)",
                "Mulch to keep the soil cool, water in the early morning or late " +
                "afternoon, and watch for wilting at midday.");
        }
        return tip("act", "Temperature is too hot (" + t + " °C)",
            "Above about 35 °C pollination fails and fruit set drops. Shade " +
            "seedlings, irrigate during the cool hours, and keep mulch on the soil.");
    }


    /* ---------- sunlight (input is average hours per day) ---------- */

    function sunlightTip(weeklyHours, stage)  /* value is hours per day */ {
        if (weeklyHours === null) { return null; }

        var perDay = Math.round(weeklyHours * 10) / 10;
        var label = perDay + " hours of sun a day on average";

        if (stage === "seedling") {
            if (perDay < 3) {
                return tip("watch", "Seedlings are getting little light (" + label + ")",
                    "Seedlings still need light to grow strong. Move the tray or " +
                    "seedbed where it gets morning sun.");
            }
            if (perDay > 8) {
                return tip("watch", "Seedlings are getting a lot of sun (" + label + ")",
                    "Protect seedlings from excessive sunlight with a temporary " +
                    "shade, and harden them gradually one week before transplanting.");
            }
            return tip("ok", "Sunlight is fine for seedlings (" + label + ")",
                "Keep the shade up and give light, not harsh midday sun.");
        }

        if (perDay < 6) {
            return tip("watch", "Sunlight looks low (" + label + ")",
                "Transplanted eggplant does best in full sun, about 6-8 hours a " +
                "day. Check for shade from nearby plants or weeds.");
        }
        return tip("ok", "Sunlight is enough (" + label + ")",
            "Full sun of about 6-8 hours a day supports good growth and fruiting.");
    }


    /* ---------- what the plant analysis says ---------- */

    function analysisTips(result, week) {
        var tips = [];
        var growth = lower(result.finalGrowth);
        var leaf = lower(result.finalLeafDistribution);
        var branch = lower(result.finalBranchDevelopment);

        if (growth === "early") {
            if (week >= 7) {
                tips.push(tip("act", "Growth looks slow for week " + week,
                    "Check the soil moisture, sunlight, fertilizer schedule and the " +
                    "leaves for pests such as fruit and shoot borer."));
            } else {
                tips.push(tip("ok", "Early growth stage",
                    "This is normal for young plants. Keep the soil evenly moist and " +
                    "avoid over-watering."));
            }
        } else if (growth === "mid") {
            tips.push(tip("ok", "Growth is steady",
                "The plant is developing well. Keep your care routine the same."));
        } else if (growth === "late") {
            tips.push(tip("ok", "Plant is well developed",
                "Focus on steady watering and protecting flowers and fruits."));
        }

        if (leaf === "sparse" && week >= 5) {
            tips.push(tip("watch", "Few leaves",
                "Look for chewed or curled leaves and for signs of pests. Follow the " +
                "fertilizer schedule in the DA guide for side dressing."));
        } else if (leaf === "dense" && week >= 5) {
            tips.push(tip("watch", "Dense leaves",
                "Prune unnecessary leaves to reduce competition for nutrients and " +
                "let air move through the plant."));
        }

        if (branch === "none" && week >= 5) {
            tips.push(tip("watch", "No branches yet",
                "Check that the plant is getting enough sun, water and nutrients."));
        } else if (branch === "developed" && week >= 5) {
            tips.push(tip("watch", "Many branches",
                "Remove the lateral branches below the split, except the branch " +
                "nearest to it (Y branch), so air can move at the base of the plant."));
        }

        return tips;
    }


    /* ---------- predicted change compared with last week ---------- */

    function trendTips(form, result) {
        var tips = [];
        var prevH = num(form.get("prevHeight"));
        var prevL = num(form.get("prevLeaves"));
        var prevB = num(form.get("prevBranches"));
        var h = num(result.predictedHeight);
        var l = num(result.predictedLeaves);
        var b = num(result.predictedBranches);

        if (prevH !== null && h !== null) {
            var d = Math.round((h - prevH) * 10) / 10;

            if (d <= 0) {
                tips.push(tip("act", "Height is not expected to increase",
                    "Predicted height is " + h + " cm, compared with " + prevH +
                    " cm last week. Check watering, sunlight and signs of disease " +
                    "such as wilting."));
            } else {
                tips.push(tip("ok", "Expected growth: +" + d + " cm this week",
                    "Measure your plant at the end of the week and compare."));
            }
        }

        if (prevL !== null && l !== null && l < prevL) {
            tips.push(tip("watch", "Fewer leaves are predicted",
                "If you did not prune, check the leaves for pests or disease."));
        }
        if (prevB !== null && b !== null && b < prevB) {
            tips.push(tip("watch", "Fewer branches are predicted",
                "This can be normal after pruning the branches below the split."));
        }

        return tips;
    }


    /* ---------- what to do this week (DA guide timeline) ---------- */
    // Transplanting is taken as the start of week 5 (30-35 days after sowing).

    function weekTip(week) {
        if (week <= 4) {
            return tip("ok", "This week: seedling care",
                "Water in the morning just enough to keep the soil moist. Thin " +
                "crowded seedlings 3-5 days after they emerge. Harden them one week " +
                "before transplanting at 30-35 days, when they have 3-4 true leaves.");
        }
        if (week === 5) {
            return tip("ok", "This week: after transplanting",
                "Replant missing or wilted hills within 3-5 days and keep the soil " +
                "moist. Irrigate at 7 days after transplanting.");
        }
        if (week === 6) {
            return tip("ok", "This week: weeding",
                "Practice regular hand weeding. Off-bar at 14 days after " +
                "transplanting is coming next week.");
        }
        if (week === 7) {
            return tip("ok", "This week: off-bar",
                "Off-bar at 14 days after transplanting, then pull the remaining " +
                "weeds between plants. Hill-up comes at 21 days.");
        }
        if (week === 8) {
            return tip("ok", "This week: hill-up and irrigation",
                "Hill-up at 21 days after transplanting and irrigate. In the dry " +
                "season, irrigate again at 30 days.");
        }
        if (week <= 11) {
            return tip("ok", "This week: flowering and fruiting",
                "Irrigate every 10 days in the dry season, or as needed in the wet " +
                "season. Watch for wilting; pull and burn infected plants.");
        }
        return tip("ok", "This week: harvest",
            "Harvest starts 46-50 days after transplanting. Pick tender young " +
            "fruits early in the morning with pruning shears, about two times a " +
            "week, to keep the plant producing.");
    }


    /* ---------- build and show ---------- */

    var ORDER = { act: 0, watch: 1, ok: 2 };
    var ICON = { act: "!", watch: "i", ok: "✓" };

    function render(items) {
        list.textContent = "";

        items.forEach(function (item) {
            var li = document.createElement("li");
            li.className = "guide-item guide-" + item.tone;

            var badge = document.createElement("span");
            badge.className = "guide-badge";
            badge.setAttribute("aria-hidden", "true");
            badge.textContent = ICON[item.tone];

            var body = document.createElement("div");

            var title = document.createElement("strong");
            title.textContent = item.title;

            var text = document.createElement("p");
            text.textContent = item.text;

            body.appendChild(title);
            body.appendChild(text);
            li.appendChild(badge);
            li.appendChild(body);
            list.appendChild(li);
        });
    }

    window.renderGuidance = function (result, form) {
        var week = num(form.get("week")) || 1;
        var stage = stageOf(week);
        var items = [];

        var t = temperatureTip(num(form.get("temperature")));
        var s = sunlightTip(num(form.get("sunlight")), stage);
        if (t) { items.push(t); }
        if (s) { items.push(s); }

        if (result.viewsAgree === false) {
            items.push(tip("watch", "Your three photos give different results",
                "The top, front and side photos do not agree. Retake them at the " +
                "same distance, in the same light, with the whole plant in the frame."));
        }

        items = items.concat(trendTips(form, result));
        items = items.concat(analysisTips(result, week));
        items.push(weekTip(week));

        // Stable sort: things that need attention come first.
        items = items
            .map(function (item, i) { return { item: item, i: i }; })
            .sort(function (a, b) {
                return ORDER[a.item.tone] - ORDER[b.item.tone] || a.i - b.i;
            })
            .map(function (x) { return x.item; });

        render(items);
        box.hidden = false;
    };

    window.clearGuidance = function () {
        list.textContent = "";
        box.hidden = true;
    };
})();

"""
Stage definitions, planning recommendations and logger field rules.

EDIT THIS FILE to change what the website shows. No other file needs to change.

IMPORTANT: every recommendation value below is a PLACEHOLDER. Water amounts were
scaled from the weekly water used in dataset/weekly_growth.csv (mL/week divided
by 7), then adjusted by temperature band. Sunlight hours follow the 7-8 h/day
range seen in that dataset. Verify all values against agronomic references
before farmers rely on them, then set VALUES_ARE_PLACEHOLDERS = False to hide
the warning banner.
"""

VALUES_ARE_PLACEHOLDERS = True


# ------------------------------------------------------------
# Stages
# ------------------------------------------------------------
# "weeks" is the list of weeks the farmer can choose in that stage.
# The mature stage is "Weeks 9-12+": weeks 13-16 are allowed for plants
# that keep growing. Change the range if you need more or fewer weeks.

STAGES = {
    "seedling": {
        "slug": "seedling",
        "name": "Seedling Stage",
        "label": "Weeks 1-4",
        "weeks": [1, 2, 3, 4],
        "blurb": "Young plants establishing roots and first true leaves.",
    },
    "vegetative": {
        "slug": "vegetative",
        "name": "Vegetative Growth Stage",
        "label": "Weeks 5-8",
        "weeks": [5, 6, 7, 8],
        "blurb": "Rapid growth of stems, branches and leaves.",
    },
    "mature": {
        "slug": "mature",
        "name": "Mature Growth Stage",
        "label": "Weeks 9-12+",
        "weeks": [9, 10, 11, 12, 13, 14, 15, 16],
        "blurb": "Fully developed plants with dense foliage.",
    },
}

STAGE_ORDER = ["seedling", "vegetative", "mature"]

ALL_WEEKS = sorted(w for s in STAGES.values() for w in s["weeks"])
DAYS_PER_WEEK = 7


def stage_for_week(week):
    for stage in STAGES.values():
        if week in stage["weeks"]:
            return stage["slug"]
    return None


# ------------------------------------------------------------
# Planning recommendations (PLACEHOLDERS)
# ------------------------------------------------------------
# Each row: temperature band (lo inclusive, hi exclusive; None = open end),
# label shown to the farmer, sunlight hours/day, water mL/day per plant, note.

RECOMMENDATIONS = {
    "seedling": [
        {"lo": None, "hi": 20, "label": "Below 20 °C",
         "sunlight": "6-8", "water": "30-35",
         "note": "Cool. Growth slows, so water lightly and keep seedlings in full light."},
        {"lo": 20, "hi": 26, "label": "20 - 25 °C",
         "sunlight": "7-8", "water": "35-40",
         "note": "Mild. Good conditions; keep the soil evenly moist."},
        {"lo": 26, "hi": 31, "label": "26 - 30 °C",
         "sunlight": "7-8", "water": "40-45",
         "note": "Ideal range for eggplant seedlings."},
        {"lo": 31, "hi": 36, "label": "31 - 35 °C",
         "sunlight": "6-7", "water": "45-55",
         "note": "Hot. Give light shade at midday and water more often."},
        {"lo": 36, "hi": None, "label": "Above 35 °C",
         "sunlight": "5-6", "water": "55-65",
         "note": "Very hot. Shade the seedlings and water early morning and late afternoon."},
    ],
    "vegetative": [
        {"lo": None, "hi": 20, "label": "Below 20 °C",
         "sunlight": "7-8", "water": "55-65",
         "note": "Cool. Growth slows; avoid overwatering."},
        {"lo": 20, "hi": 26, "label": "20 - 25 °C",
         "sunlight": "7-8", "water": "65-80",
         "note": "Mild. Steady growth; water regularly."},
        {"lo": 26, "hi": 31, "label": "26 - 30 °C",
         "sunlight": "7-8", "water": "70-85",
         "note": "Ideal range for vegetative growth."},
        {"lo": 31, "hi": 36, "label": "31 - 35 °C",
         "sunlight": "6-7", "water": "85-105",
         "note": "Hot. Water more and watch for wilting at midday."},
        {"lo": 36, "hi": None, "label": "Above 35 °C",
         "sunlight": "5-6", "water": "100-120",
         "note": "Very hot. Provide shade and split watering into two times a day."},
    ],
    "mature": [
        {"lo": None, "hi": 20, "label": "Below 20 °C",
         "sunlight": "7-8", "water": "80-100",
         "note": "Cool. Growth and fruiting slow down; water less often."},
        {"lo": 20, "hi": 26, "label": "20 - 25 °C",
         "sunlight": "7-8", "water": "100-120",
         "note": "Mild. Keep watering consistent."},
        {"lo": 26, "hi": 31, "label": "26 - 30 °C",
         "sunlight": "7-8", "water": "110-135",
         "note": "Ideal range for mature plants."},
        {"lo": 31, "hi": 36, "label": "31 - 35 °C",
         "sunlight": "6-7", "water": "130-160",
         "note": "Hot. Increase water; mulch to keep the soil cool."},
        {"lo": 36, "hi": None, "label": "Above 35 °C",
         "sunlight": "5-6", "water": "155-185",
         "note": "Very hot. Shade in the afternoon and water in the early morning and evening."},
    ],
}


# ------------------------------------------------------------
# Daily measurement fields
# ------------------------------------------------------------
# kind: "int" or "float". min/max are the accepted range (inclusive).
# These match the columns used by the prediction model
# (dataset/weekly_growth.csv). Water is recorded per DAY; the weekly summary
# also shows the estimated weekly total because the prediction page uses mL/week.

FIELDS = [
    {"key": "height", "label": "Plant height", "unit": "cm", "kind": "float", "min": 0, "max": 300},
    {"key": "leaves", "label": "Number of leaves", "unit": "", "kind": "int", "min": 0, "max": 1000},
    {"key": "branches", "label": "Number of branches", "unit": "", "kind": "int", "min": 0, "max": 200},
    {"key": "temperature", "label": "Temperature", "unit": "°C", "kind": "float", "min": 0, "max": 60},
    {"key": "sunlight", "label": "Sunlight exposure", "unit": "hours", "kind": "float", "min": 0, "max": 24},
    {"key": "water", "label": "Water given (per day)", "unit": "mL", "kind": "float", "min": 0, "max": 10000},
]

FIELD_KEYS = [f["key"] for f in FIELDS]
FIELD_BY_KEY = {f["key"]: f for f in FIELDS}

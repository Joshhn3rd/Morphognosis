"""
Stage definitions, planning recommendations and logger field rules.

EDIT THIS FILE to change what the website shows. No other file needs to change.

WHERE THE RECOMMENDATIONS COME FROM
  Temperature bands - DA-RFO 02 Eggplant Production Guide (2017): growth
      21-30 C; Eggplant Growth Science slides: flowers/pollen drop and fruit set
      fails below ~16 C and above ~35 C.
  Sunlight hours - the guide says seedlings need shade and hardening and the
      field should be fully exposed to sun. It gives no hours, so the hours are
      CALIBRATED: a 4-6 h direct-sun window for seedlings and 6-8 h of full
      sun for transplanted plants (common extension guidance for eggplant).
  Water (mL per plant per day) - CALIBRATED, not measured:
        water = ET0 x Kc x plant area x 1000 (+/- 10 %)
      ET0 (mm/day) rises with temperature: 2.5 / 3.2 / 4.2 / 5.3 / 6.0 for the
      five bands. Kc (FAO-56) = 0.6 seedling, 0.8 vegetative, 1.05 mature.
      Plant area = 0.01 m2 per seedling (potlet), 0.25 m2 per field plant
      (50 cm x 50 cm hills in the DA guide).
  The guide's "35-40 mL of water per week" and the slides' 1,000-8,500 mL/day
  could not be reconciled with each other, so the estimate above is used.
  Verify with your adviser, then edit the numbers below if needed.
"""

VALUES_ARE_PLACEHOLDERS = False
VALUES_ARE_ESTIMATES = True


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
        "blurb": "Sow, thin and harden seedlings. Transplant at 30-35 days with 3-4 true leaves.",
    },
    "vegetative": {
        "slug": "vegetative",
        "name": "Vegetative Growth Stage",
        "label": "Weeks 5-8",
        "weeks": [5, 6, 7, 8],
        "blurb": "After transplanting: irrigate, weed, hill-up and prune for stems, branches and leaves.",
    },
    "mature": {
        "slug": "mature",
        "name": "Mature Growth Stage",
        "label": "Weeks 9-12+",
        "weeks": [9, 10, 11, 12, 13, 14, 15, 16],
        "blurb": "Flowering and fruiting. Harvest starts 46-50 days after transplanting.",
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
# Planning recommendations (calibrated estimates, see top of file)
# ------------------------------------------------------------
# Each row: temperature band (lo inclusive, hi exclusive; None = open end),
# label shown to the farmer, sunlight hours/day, water mL/day per plant, note.

RECOMMENDATIONS = {
    "seedling": [
        {"lo": None, "hi": 16, "label": "Below 16 °C",
         "sunlight": "5-6", "water": "10-15",
         "note": "Too cold. Growth slows. Give morning sun and water very lightly."},
        {"lo": 16, "hi": 21, "label": "16 - 20 °C",
         "sunlight": "5-6", "water": "15-20",
         "note": "Cool. Keep the soil just moist to avoid damping-off."},
        {"lo": 21, "hi": 31, "label": "21 - 30 °C",
         "sunlight": "4-6", "water": "25-30",
         "note": "Ideal range. Water in the morning and keep the temporary shade up."},
        {"lo": 31, "hi": 36, "label": "31 - 35 °C",
         "sunlight": "3-5", "water": "30-35",
         "note": "Hot. Shade the seedlings at midday and check the soil twice a day."},
        {"lo": 36, "hi": None, "label": "Above 35 °C",
         "sunlight": "2-4", "water": "35-40",
         "note": "Very hot. Keep under shade, water early and late, and do not harden now."},
    ],
    "vegetative": [
        {"lo": None, "hi": 16, "label": "Below 16 °C",
         "sunlight": "6-8", "water": "450-550",
         "note": "Too cold. Growth and flowering slow down. Avoid over-watering."},
        {"lo": 16, "hi": 21, "label": "16 - 20 °C",
         "sunlight": "6-8", "water": "600-700",
         "note": "Cool. Keep the soil moist but not soggy."},
        {"lo": 21, "hi": 31, "label": "21 - 30 °C",
         "sunlight": "6-8", "water": "750-900",
         "note": "Ideal range for growth. Irrigate on the guide's schedule (7, 21, 30 days after transplanting)."},
        {"lo": 31, "hi": 36, "label": "31 - 35 °C",
         "sunlight": "6-8", "water": "950-1150",
         "note": "Hot. Mulch to keep the soil cool and watch for wilting at midday."},
        {"lo": 36, "hi": None, "label": "Above 35 °C",
         "sunlight": "6-7", "water": "1100-1300",
         "note": "Very hot. Water early morning and late afternoon; flowers may drop."},
    ],
    "mature": [
        {"lo": None, "hi": 16, "label": "Below 16 °C",
         "sunlight": "6-8", "water": "600-700",
         "note": "Too cold. Flowers and pollen drop and fruit set fails. Water less often."},
        {"lo": 16, "hi": 21, "label": "16 - 20 °C",
         "sunlight": "6-8", "water": "750-900",
         "note": "Cool. Keep watering steady; fruiting is slower."},
        {"lo": 21, "hi": 31, "label": "21 - 30 °C",
         "sunlight": "6-8", "water": "1000-1200",
         "note": "Ideal range for flowering and fruiting. Keep the soil evenly moist."},
        {"lo": 31, "hi": 36, "label": "31 - 35 °C",
         "sunlight": "6-8", "water": "1250-1550",
         "note": "Hot. Increase water and keep mulch on; fruits need leaf cover from sun scald."},
        {"lo": 36, "hi": None, "label": "Above 35 °C",
         "sunlight": "6-7", "water": "1400-1750",
         "note": "Very hot. Pollination fails. Water in the cool hours; harvest early in the morning."},
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

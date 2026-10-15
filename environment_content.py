"""
Text and images for the Sunlight, Temperature and Water pages (eggplant only).

EDIT THIS FILE to change what those pages say. No other file needs to change.
Images live in static/images (taken from the "Eggplant Growth Science" slides).

Where the numbers come from
---------------------------
DA-RFO 02  Department of Agriculture, Regional Field Office No. 02, High Value
           Crops Development Program (2017). Eggplant Production Guide.
           Source of the temperature ranges, seedling care, transplanting age,
           irrigation schedule and harvest timing.
FAO-56     Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). Crop
           evapotranspiration: Guidelines for computing crop water
           requirements. FAO Irrigation and Drainage Paper 56.
           Basis of the water estimate (see stage_config.py).
"""

SOURCE_DA = (
    "Department of Agriculture, Regional Field Office No. 02, High Value Crops "
    "Development Program (2017). Eggplant Production Guide."
)
SOURCE_FAO = (
    "Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). Crop "
    "evapotranspiration - Guidelines for computing crop water requirements. "
    "FAO Irrigation and Drainage Paper 56."
)
SOURCE_SLIDES = "Eggplant Growth Science (project slides)."


FACTORS = {

    "sunlight": {
        "slug": "sunlight",
        "title": "Sunlight",
        "heading": "Sunlight Exposure",
        "card_image": "sunlight.jpg",
        "background": "sunlight.jpg",
        "figure": "sunlight.jpg",
        "figure_alt": "Eggplant plant in full sun with flowers and two fruits; roots "
                      "take minerals from the soil.",
        "accent": "yellow",
        "intro": "How sunlight helps the eggplant at each stage",
        "steps": [
            {
                "tab": "Seedling",
                "title": "1. Seedling stage (nursery)",
                "text": "Eggplant seedlings are raised in a seedbed or seedling tray for "
                        "30-35 days, until they have 3-4 true leaves. The DA guide asks "
                        "growers to protect seedlings from excessive sunlight and rain "
                        "with a temporary shade, then harden them before transplanting.",
                "impacts_label": "What to do with sunlight at this stage:",
                "impacts": [
                    ("Give light, not harsh midday sun",
                     "Seedlings still need light to make food, but a shade about 120 cm "
                     "high on the east side and 60 cm on the west side keeps the "
                     "strongest sun off the young plants."),
                    ("Harden one week before transplanting",
                     "On day 1 expose seedlings to direct sun only until 10 o'clock in "
                     "the morning, then add more time each day until they can take "
                     "the full day's sun without wilting severely."),
                ],
            },
            {
                "tab": "Vegetative",
                "title": "2. Vegetative growth (after transplanting)",
                "text": "After transplanting, the plant builds stems, branches and leaves. "
                        "The seedbed and field should be fully exposed to sunlight.",
                "impacts_label": "Positive impacts of sunlight at this stage:",
                "impacts": [
                    ("Powers photosynthesis",
                     "Leaves use sunlight, carbon dioxide and water to make sugar. The "
                     "plant uses that sugar as energy to grow taller and to add "
                     "leaves and branches."),
                    ("Supports root activity",
                     "A healthy, well-lit plant keeps its roots active in absorbing "
                     "water and minerals from the soil."),
                    ("Needs open air around the base",
                     "Pruning the lateral branches below the first split, except the "
                     "Y branch, lets light and air reach the plant and lowers fungal "
                     "and bacterial disease."),
                ],
            },
            {
                "tab": "Flowering & fruiting",
                "title": "3. Flowering and fruiting",
                "text": "Purple flowers form and fruits begin to develop. Eggplant keeps "
                        "its best fruit set within its comfortable temperature range, "
                        "so sunlight should come with good water supply.",
                "impacts_label": "Positive impacts of sunlight at this stage:",
                "impacts": [
                    ("Feeds the developing fruit",
                     "Sugar made in the leaves is moved to the growing fruits."),
                    ("Double-row planting protects fruits",
                     "Most farmers plant eggplant in double rows because the leaves give "
                     "developing fruits protection against sun scalding."),
                    ("Too much heat is harmful",
                     "Above about 35 °C, flowers and pollen drop and fruit set fails. "
                     "See the Temperature page."),
                ],
            },
            {
                "tab": "Harvest",
                "title": "4. Harvest",
                "text": "Harvesting starts 46-50 days after transplanting, depending on "
                        "the variety and the intended use of the fruits.",
                "impacts_label": "Sunlight and heat at harvest:",
                "impacts": [
                    ("Harvest early in the morning",
                     "Pick tender, young fruits in the early morning and protect them "
                     "from sun, rain and mechanical damage."),
                    ("Keep the plant producing",
                     "Harvest all fruits from the plant, about two times a week, to "
                     "prolong the fruiting period."),
                ],
            },
        ],
        "source": SOURCE_DA + " Photosynthesis diagram: " + SOURCE_SLIDES,
        "source_url": None,
        "figure_credit": "Illustration: Eggplant Growth Science slides",
    },

    "temperature": {
        "slug": "temperature",
        "title": "Temperature",
        "heading": "Temperature",
        "card_image": "temperature.jpg",
        "background": "temperature.jpg",
        "figure": "temperature.jpg",
        "figure_alt": "Eggplant plant in warm sun showing flowers, leaves, stem and roots.",
        "accent": "purple",
        "blocks": [
            {
                "title": "Optimum range:",
                "sub": "(21 - 30 °C)",
                "text": "Eggplant grows best at 21 to 30 °C. Seeds germinate best at "
                        "20 to 30 °C, and the soil should be 24 to 32 °C. Within this "
                        "range the plant grows normally and sets fruit.",
            },
            {
                "title": "Too cold",
                "sub": "(below about 16 °C):",
                "text": "Eggplant is a warm-season crop. In cool weather growth slows "
                        "and flowers and pollen drop, so fruit set fails. Water "
                        "lightly because the plant uses less water.",
            },
            {
                "title": "Too hot",
                "sub": "(above about 35 °C):",
                "text": "Extreme heat disrupts pollination and prevents fruit set. "
                        "It also limits leaf size, reduces stomata function and slows "
                        "stem length and thickening. Mulch, shade seedlings and "
                        "irrigate in the cool hours of the day.",
            },
            {
                "title": "Effects of heat on each plant part",
                "sub": None,
                "text": "Flowers and fruit: pollination fails. Leaves: smaller, with "
                        "poor stomata function. Stem: slower length and thickness "
                        "growth. Roots and germination: seeds sprout best in 24-32 °C "
                        "soil.",
            },
        ],
        "source": SOURCE_DA + " Heat-stress effects: " + SOURCE_SLIDES,
        "source_url": None,
        "figure_credit": "Illustration: Eggplant Growth Science slides",
    },

    "water": {
        "slug": "water",
        "title": "Water",
        "heading": "Water",
        "card_image": "water.jpg",
        "background": "water.jpg",
        "figure": "water.jpg",
        "figure_alt": "Eggplant plant with blue arrows showing water moving from the roots "
                      "up through the stem to the leaves.",
        "accent": "none",
        "blocks": [
            {
                "title": "How the plant uses water:",
                "sub": None,
                "text": "Roots absorb water and minerals from the soil. The water "
                        "travels up through the stem, and water vapor leaves through "
                        "pores in the leaves (transpiration). This movement carries "
                        "minerals to the leaves and keeps the plant cool.",
            },
            {
                "title": "When to irrigate:",
                "sub": "(DA guide)",
                "text": "Water the beds 2 days before transplanting, and water newly "
                        "transplanted seedlings immediately. In the dry season, "
                        "irrigate at 7, 21 and 30 days after transplanting, then every "
                        "10 days. In the wet season, irrigate as the need arises. "
                        "Mulched eggplant needs less frequent irrigation.",
            },
            {
                "title": "Seedlings:",
                "sub": None,
                "text": "Water in the morning, just enough to keep the soil moist. "
                        "Over-watering favors damping-off and weak seedlings.",
            },
            {
                "title": "How much water:",
                "sub": "(estimate per plant per day)",
                "text": "The amounts on the stage pages are estimates, not measured "
                        "values. They come from the water an eggplant is expected "
                        "to lose through its leaves and soil (FAO-56 method), the "
                        "50 cm x 50 cm planting distance in the DA guide, and the day's "
                        "temperature. A seedling needs roughly 15-40 mL a day, while a "
                        "mature plant in the field may need about 1-1.7 liters. "
                        "Rain, soil type and mulch change the real need.",
            },
        ],
        "source": SOURCE_DA + " " + SOURCE_FAO,
        "source_url": None,
        "figure_credit": "Illustration: Eggplant Growth Science slides",
    },
}

ORDER = ["sunlight", "temperature", "water"]

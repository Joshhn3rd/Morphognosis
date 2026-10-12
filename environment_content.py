"""
Text and images for the Sunlight, Temperature and Water pages.

EDIT THIS FILE to change what those pages say. No other file needs to change.
Images live in static/images.
"""

SOURCE_SUNLIGHT = (
    "Stanikzai, A. S. (2025, December 11). The positive impact of sunlight on "
    "crops in those four different stages. LinkedIn."
)
SOURCE_SUNLIGHT_URL = (
    "https://www.linkedin.com/posts/ajmalsohailstanikzai_the-positive-impact-of-"
    "sunlight-on-crops-activity-7404873076821188608-OrMJ"
)


FACTORS = {

    "sunlight": {
        "slug": "sunlight",
        "title": "Sunlight",
        "heading": "Sunlight Exposure",
        "card_image": "sunlight.jpg",
        "background": "sunlight.jpg",
        "figure": "info-sunlight.jpg",
        "figure_alt": "Infographic: the positive impact of sunlight on crops in four stages "
                      "- germination, growing, fruiting and ripening.",
        "accent": "yellow",
        "intro": "The Positive Impact of Sunlight on Crops in Those Four Different Stages",
        "steps": [
            {
                "tab": "Germination",
                "title": "1. Germination Stage",
                "text": "In the germination stage, seeds absorb water and begin to sprout. "
                        "Although most seeds can germinate in darkness, sunlight becomes "
                        "important immediately after the seedling emerges.",
                "impacts_label": "Positive impacts of sunlight in the germination stage:",
                "impacts": [
                    ("Supports early photosynthesis",
                     "Once the young shoot breaks the soil surface, sunlight allows it to "
                     "start making its own food."),
                    ("Prevents weak seedlings",
                     "Adequate sunlight reduces etiolation (stretching and becoming pale "
                     "due to lack of light), helping seedlings grow strong and healthy."),
                    ("Enhances root and shoot development",
                     "Light encourages balanced growth between roots and shoots, preparing "
                     "the plant for the next stages."),
                ],
            },
            {
                "tab": "Growing",
                "title": "2. Growing Stage",
                "text": "During this stage, the plant develops leaves, stems, and roots. "
                        "This is when sunlight has one of its greatest impacts on crop "
                        "productivity.",
                "impacts_label": "Positive impacts of sunlight in the growing stage:",
                "impacts": [
                    ("Boosts photosynthesis",
                     "More sunlight means more energy for the plant to produce "
                     "carbohydrates, leading to faster and stronger growth."),
                    ("Improves leaf size and strength",
                     "Adequate sunlight increases chlorophyll content, making leaves "
                     "greener and more efficient in photosynthesis."),
                    ("Strengthens plant structure",
                     "Sunlight helps plants produce sturdier stems, allowing them to "
                     "resist wind, pests, and diseases."),
                    ("Increases nutrient uptake",
                     "Light supports root activity, improving absorption of water and "
                     "essential nutrients."),
                ],
            },
            {
                "tab": "Fruiting",
                "title": "3. Fruiting Stage",
                "text": "This stage includes flower formation, pollination, and fruit "
                        "development. Sunlight influences the quantity and quality of "
                        "fruits produced.",
                "impacts_label": "Positive impacts of sunlight in the fruiting stage:",
                "impacts": [
                    ("Enhances flower formation",
                     "Plants exposed to the right amount of sunlight produce more "
                     "flowers, increasing fruit potential."),
                    ("Improves pollination",
                     "Sunlight attracts pollinators like bees, resulting in better "
                     "fruit set."),
                    ("Strengthens fruit development",
                     "Adequate sunlight promotes sugar production, which is transported "
                     "to fruits during growth."),
                    ("Reduces disease prevalence",
                     "Sunlight helps reduce humidity around plants, decreasing the risk "
                     "of fungal infections during fruit formation."),
                ],
            },
            {
                "tab": "Ripening",
                "title": "4. Ripening Stage",
                "text": "Ripening is when fruits develop their final color, flavor, and "
                        "aroma.",
                "impacts_label": "Positive impacts of sunlight in the ripening stage:",
                "impacts": [
                    ("Improves fruit color",
                     "Sunlight stimulates pigment formation (such as carotenoids and "
                     "anthocyanins), making fruits more attractive and marketable."),
                    ("Increases sweetness",
                     "More sunlight boosts sugar concentration, improving taste and "
                     "nutritional value."),
                    ("Enhances aroma and flavor",
                     "Sunlight promotes chemical reactions that produce natural fruit "
                     "aromas."),
                    ("Speeds up ripening",
                     "Warmth and light accelerate physiological processes that lead to "
                     "full ripening."),
                    ("Improves nutritional quality",
                     "Sunlight increases vitamins such as Vitamin C in fruits and "
                     "vegetables."),
                ],
            },
        ],
        "source": SOURCE_SUNLIGHT,
        "source_url": SOURCE_SUNLIGHT_URL,
        "figure_credit": None,
    },

    "temperature": {
        "slug": "temperature",
        "title": "Temperature",
        "heading": "Temperature",
        "card_image": "temperature.jpg",
        "background": "temperature.jpg",
        "figure": "info-temperature.jpg",
        "figure_alt": "Infographic: heat stress on a plant - oxidative damage, higher "
                      "energy use and reduced growth, compared with a plant that "
                      "maintains photosynthesis under hot conditions.",
        "accent": "purple",
        "blocks": [
            {
                "title": "Optimum Range:",
                "sub": None,
                "text": "Most plants grow best at daytime temperatures between 15°C and "
                        "25°C (59°F to 77°F), though specific requirements vary by "
                        "species and stage of life.",
            },
            {
                "title": "Too Cold",
                "sub": "(<7°C/45°F):",
                "text": "Growth slows down drastically, metabolic rates drop, and freezing "
                        "temperatures (< 0°C) can cause ice crystals to form inside "
                        "cells, leading to tissue death.",
            },
            {
                "title": "Too Hot",
                "sub": "(>30°C–35°C+):",
                "text": "High temperatures accelerate respiration faster than "
                        "photosynthesis can produce energy, leading to heat stress, "
                        "wilt, or reduced crop yields.",
            },
        ],
        "source": None,
        "source_url": None,
        "figure_credit": "Infographic: Ravensa Next",
    },

    "water": {
        "slug": "water",
        "title": "Water",
        "heading": "Water",
        "card_image": "water.jpg",
        "background": "water.jpg",
        "figure": "info-water.jpg",
        "figure_alt": "Diagram: water and minerals are absorbed by the roots, travel up "
                      "through the plant, and are released as vapor from leaf pores in "
                      "transpiration.",
        "accent": "none",
        "paragraphs": [
            "Water is essential for plant growth because it supports photosynthesis, "
            "nutrient uptake, cell expansion, and the transport of minerals and sugars "
            "throughout the plant. Adequate water maintains turgor pressure, which keeps "
            "cells firm and allows leaves, stems, and roots to grow properly. It also "
            "helps regulate plant temperature through transpiration and enables stomata "
            "to open for carbon dioxide uptake.",
            "When water is limited, plants close their stomata, reducing photosynthesis "
            "and transpiration. Continued water stress causes loss of turgor, wilting, "
            "reduced leaf expansion, shallower or altered root growth, and lower biomass "
            "and yield. Severe or prolonged drought can slow or stop growth and reduce "
            "seed, fruit, and grain production.",
        ],
        "source": None,
        "source_url": None,
        "figure_credit": None,
    },
}

ORDER = ["sunlight", "temperature", "water"]

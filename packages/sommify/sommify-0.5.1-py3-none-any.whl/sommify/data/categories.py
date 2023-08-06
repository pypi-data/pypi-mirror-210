# from utils import with_plural, to_regex
import re

from ..utils import to_regex, with_plural

# from data.ingredient_categories import fruits, vegetables, legumes, herbs
from .ingredient_categories import vegetables

# from data.ingredients import dictionary as ing_dict
from .ingredients import dictionary as ing_dict

# from data.meat import dictionary as meat_dict
from .meat import dictionary as meat_dict

proteins = list(meat_dict.keys())
pasta = ing_dict["pasta"]

drink_list = with_plural(
    [
        "slushy",
        "slushie",
        "colada",
        "old fashioned",
        "bitter",
        "whiskey",
        "liqueur",
        "cider",
        "cappuccino",
        "frappuccino",
        "coffee",
        "espresso",
        "cocktail",
        "beer",
        "wine",
        "rootbeer",
        "drink",
        "juice",
        "tea",
        "milk",
        "moccha",
        "shake",
        "milkshake",
        "smoothie",
        "cocoa",
        "margarita",
        "mojito",
        "smoothie",
        "gin",
        "lemonade",
        "martini",
        "soda",
        "punch",
        "fizzy",
        "ouzo",
        "mocha",
        "latte",
        "frappe",
        "limeade",
        "cafe",
        "irish cream",
        "café",
        "frappé",
        "cordial",
        "chai",
        "lassi",
        "aqua thunder",
        "limoncello",
        "tequini",
        "cactus bite",
        "the yellow jacket",
        "caribbean twist",
        "brazillian sunset",
    ]
)
soup_list = with_plural(
    [
        "minestrone",
        "soup",
        "chowder",
        "bouillabaisse",
        "gazpacho",
        "bisque",
        "bouillon",
        "broth",
        "consomme",
        "consommé",
        "velouté",
        "veloute",
        "vichyssoise",
        "skink",
        "laksa",
        "ramen",
        "goulash",
        "stew",
        "bourguignon",
        "rogan josh",
    ]
)
niche_list = with_plural(
    [
        "vinaigrette",
        "horseradish",
        "compote",
        "sauce",
        "marinade",
        "dip",
        "jam",
        "queso",
        "jus",
        "dressing",
        "bread",
        "spread",
        "preserve",
        "stock",
        "bouillon",
        "salsa",
        "gravy",
    ]
)
dessert_list = with_plural(
    [
        "apple pie",
        "semifreddo",
        "waffle",
        "crepe",
        "pudding",
        "french toast",
        "torta",
        "tiramisu",
        "sundae",
        "madeleine",
        "ice cream",
        "cookie",
        r"muffin",
        r"bar",
        r"cupcake",
        r"brownie",
        r"cheesecake",
        r"pancake",
        "tart",
        "rugelach",
        "chiffon cake",
        r"biscuit",
        r"scone",
        "sorbet",
        "biscotti",
        "galette",
        "granola",
        "buttercream",
        r"doughnut",
        "crumble",
        "shortbread",
        r"mousse",
        "baklava",
        "donut",
    ]
)
sandwich_list = with_plural(
    [
        "panini",
        "sandwich",
        "burrito",
        "burger",
        "taco",
        "bruschetta",
        "baguette",
        "wrap",
        r"hot ?dog",
        "enchilada",
        "ciabatta",
    ]
)
exceptions = ["stock", "broth", "bouillon", "beefsteak"]

title_map = {
    "seafood": to_regex(["ceviche"]),
    "sandwich": to_regex(sandwich_list),
    "pasta": to_regex(pasta + ["pasta", "alfredo"]),
    "sausage": to_regex(["sausage", "sausages", "chorizo"]),
    "casserole": to_regex(["casserole"]),
    # "dessert": to_regex(dessert_list),
    "soup": to_regex(soup_list),
    "pizza": to_regex([r"pizza$", r"calzone$", r"buffalina$", r"margherita$"]),
}

ing_keys = proteins + ["pasta"]

ing_map = {"spicy food": "spicy pepper"}

root_map = {
    "sandwich": to_regex(sandwich_list),
    "vegetarian": to_regex(
        with_plural(
            vegetables + ["mushroom", "portobell", "brussels sprouts", "tofu", "beans"]
        )
    ),
    "salad": to_regex(["(?<!fruit )salad"]),
    "pasta": to_regex(pasta + ["pasta", "alfredo"]),
    # "dessert": to_regex(dessert_list),
    "niche": to_regex(niche_list),
    "soup": to_regex(soup_list),
    "drink": rf"{to_regex(drink_list)}$",
    "pizza": to_regex(["pizza", "calzone", "buffalina", "margherita"]),
    "sushi": to_regex(
        ["nigiri", "sashimi", "chirashi", "oshizushi", "temaki", "uramaki", "sushi"]
    ),
}


def is_dessert(parsedPhrases):
    def is_dessert_ing(name, quantity):
        key_list = [
            "syrup",
            "molasses",
            "chocolate",
            "caramel",
            r"nut$",
            "cocoa",
            # "sugar",
            "milk",
            "cinnamon",
            "vanilla",
            "honey",
        ]
        if name == "sugar" and quantity and quantity > 50:
            return True

        if re.search(rf"\b(?:{r'|'.join(key_list)})\b", name):
            return True
        return False

    def is_non_dessert_ing(name):
        # herb_exceptions = r"(?:mint|basil|rosemary|thyme)"

        key_list = (
            # [h for h in herbs if not re.search(herb_exceptions, h)]
            proteins
            + ["pepper", "garlic", "onion", "shallot", "spinach", "potato", "tofu"]
            + [
                "monterey jack cheese",
                "mexican cheese",
                "feta cheese",
                "mozzarella cheese",
                "pecorino cheese",
                "gruyere cheese",
                "cottage cheese",
                "pepper jack cheese",
                "cheddar cheese",
                "parmesan cheese",
            ]
        )
        if re.search(rf"\b(?:{r'|'.join(key_list)})\b", name):
            return True
        return False

    if all(
        not ing or not is_dessert_ing(ing["simple"], ing["quantity"])
        for ing in parsedPhrases
    ):
        return False

    if any(ing and is_non_dessert_ing(ing["simple"]) for ing in parsedPhrases):
        return False

    return True


function_map = {"dessert": is_dessert}


models = {
    "fish": [
        "seafood",
        "tuna",
        "lean fish",
        "salmon",
        "crustacean",
        "fatty fish",
        "other seafood",
        "octopus",
    ],
    "white-meat": [
        "poultry",
    ],
    "red-meat": [
        "game bird",
        "beef",
        "pork",
        "sausage",
        "game",
        "lamb",
        "bacon",
        "liver",
    ],
    "sweets": [
        "dessert",
    ],
    "other": [
        "soup",
        "spicy food",
        "niche",
        "ham",
        "sandwich",
        "pizza",
        "pasta",
        "casserole",
        "vegetarian",
        "salad",
    ],
}

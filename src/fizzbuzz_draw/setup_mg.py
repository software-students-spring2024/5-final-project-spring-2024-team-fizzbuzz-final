"""
methods to create and delete collections
"""

from dotenv import dotenv_values

# Loading development configurations
config = dotenv_values(".env")


def add_default_themes(se5_db):
    """
    add the default prompt collections
    """
    se5_db["theme_packs"].insert_one(
        {
            "theme": "fruits",
            "prompts": [
                "apple",
                "orange",
                "strawberry",
                "banana",
                "coconut",
                "cherry",
                "grape",
                "pear",
            ],
        }
    )

    se5_db["theme_packs"].insert_one(
        {
            "theme": "desserts",
            "prompts": ["cookie", "icecream", "custard", "pie", "donut", "eclair"],
        }
    )

    se5_db["theme_packs"].insert_one(
        {
            "theme": "transportation",
            "prompts": [
                "car",
                "train",
                "plane",
                "bus",
                "motorcycle",
                "bicycle",
                "skateboard",
            ],
        }
    )


def start_mgd(se5_db):
    """
    set up collections
    """

    if "theme_packs" not in se5_db:
        se5_db.add_collection("theme_packs", "SE_PROJECT5_theme_packs")

    if "rooms" not in se5_db:
        se5_db.add_collection("rooms", "SE_PROJECT5_rooms")

    if "scores" not in se5_db:
        se5_db.add_collection("scores", "SE_PROJECT5_scores")

    add_default_themes(se5_db)


def end_mgd(dbase, se5_db):
    """
    delete all collections created
    """

    se5_db.remove_collection("rooms")
    se5_db.remove_collection("theme_packs")
    se5_db.remove_collection("scores")
    se5_db.remove_collections()

    dbase.nested_collections.delete_one({"name": "SE_PROJECT5"})

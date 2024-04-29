"""
methods to create and delete collections
"""

from dotenv import dotenv_values

# Loading development configurations
config = dotenv_values(".env")


def start_mgd(se5_db):
    """
    set up collections
    """

    _ = ""

    if "_" not in se5_db:
        se5_db.add_collection("_", "SE_PROJECT5__")
    _._ = se5_db[""]


def end_mgd(db, se5_db):
    """
    delete all collections created
    """

    _ = ""

    try:
        _._.drop()
    except AttributeError:
        print("Couldn't delete")
        return

    se5_db.remove_collection("_")
    se5_db.remove_collection("_")

    db.nested_collections.delete_one({"name": "SE_PROJECT5"})

    return

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

    if "rooms" not in se5_db:
        se5_db.add_collection("rooms", "SE_PROJECT5_rooms")


def end_mgd(dbase, se5_db):
    """
    delete all collections created
    """

    se5_db.remove_collection("rooms")
    se5_db.remove_collections()

    dbase.nested_collections.delete_one({"name": "SE_PROJECT5"})

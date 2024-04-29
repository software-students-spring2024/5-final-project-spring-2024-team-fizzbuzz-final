"""
methods to create and delete collections
"""

from dotenv import dotenv_values
from drawing import Drawing

# Loading development configurations
config = dotenv_values(".env")


def start_mgd(se5_db):
    """
    set up collections
    """

    if "drawings" not in se5_db:
        se5_db.add_collection("drawings", "SE_PROJECT5_drawings")
    Drawing.drawings = se5_db["drawings"]


def end_mgd(dbase, se5_db):
    """
    delete all collections created
    """

    try:
        Drawing.drawings.drop()
    except AttributeError:
        print("Couldn't delete")
        return

    se5_db.remove_collection("drawings")
    se5_db.remove_collections()

    dbase.nested_collections.delete_one({"name": "SE_PROJECT5"})

    return

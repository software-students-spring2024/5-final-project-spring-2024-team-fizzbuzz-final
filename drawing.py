"""
class + tools to save drawings
"""

from __future__ import annotations
from typing import Dict, AnyStr, List
from bson.objectid import ObjectId
from pymongo import collection


class Drawing:
    """
    Class implementation for Drawing
    """

    drawings: collection

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        prompt: AnyStr,
        drawer: AnyStr,
        guesser: AnyStr = None,
        drawing: List = None,
        time_to_guess: float = None,
        idef: ObjectId = None,
    ):
        """
        initialize drawing
        """
        self.prompt = prompt
        self.drawer = drawer
        self.guesser = guesser
        self.drawing = drawing
        self.time_to_guess = time_to_guess
        if not idef:
            self.idef = Drawing.drawings.insert_one(self.to_bson()).inserted_id

    def to_bson(self) -> Dict:
        """
        Convert object to BSON
        """
        bson_dict = {}
        if self.idef:
            bson_dict["_id"] = self.idef
        bson_dict["prompt"] = self.prompt
        bson_dict["drawer"] = self.drawer
        bson_dict["guesser"] = self.guesser
        bson_dict["drawing"] = self.drawing
        bson_dict["time_to_guess"] = self.time_to_guess
        return bson_dict

    def get_time_to_guess(self):
        """
        getter to acquire time_to_guess
        """
        return self.time_to_guess

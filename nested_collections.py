"""
nested_collections implementation for mongodb database management and organization
"""

from typing import AnyStr
from pymongo import MongoClient, collection


class NestedCollection:
    """
    class implementation of NestedCollection
    """

    def __init__(self, name: AnyStr, root_db: MongoClient) -> None:
        """
        initializer
        """
        self.root_db = root_db
        self.name = name
        self.config = self.root_db.nested_collections.find_one({"name": name})
        self.dict = {}
        for col in self.config["children"]:
            # collection[0] : pseudonym - collection[1] : collection name
            self.dict[col[0]] = col[1]

    def name_from_pseudonym(self, pseudonym: AnyStr) -> AnyStr:
        """
        get mapping between pseudonym and name
        """
        return self.dict[pseudonym]

    def list_collections(self) -> None:
        """
        list all collection
        """
        print(self.config["children"])

    def add_collection(self, pseudonym: AnyStr, name: AnyStr) -> None:
        """
        add a collection
        """
        self.config["children"].append((pseudonym, name))
        self.dict[pseudonym] = name
        self.root_db.nested_collections.update_one(
            {"name": self.name}, {"$set": {"children": self.config["children"]}}
        )

    def remove_collection(self, pseudonym: AnyStr, drop=True) -> None:
        """
        remove a collection
        """
        for i in range(len(self.config["children"])):
            if self.config["children"][i][0] == pseudonym:
                if drop:
                    self[pseudonym].drop()
                del self.dict[pseudonym]
                self.config["children"].pop(i)
                self.root_db.nested_collections.update_one(
                    {"name": self.name}, {"$set": {"children": self.config["children"]}}
                )
                return

    def __getitem__(self, pseudonym) -> collection:
        """
        get a collection by psuedonym
        """
        try:
            return self.root_db.get_collection(self.dict[pseudonym])
        except KeyError:
            print("Collection", pseudonym, "doesn't exist...")
            return None

    def __contains__(self, pseudonym):
        """
        check if collection by pseydonym exists
        """
        return pseudonym in self.dict

    def remove_collections(self) -> None:
        """
        removes all collections
        """

        self.dict = {}
        self.config["children"] = []

        self.root_db.nested_collections.update_one(
            {"name": self.name}, {"$set": {"children": self.config["children"]}}
        )

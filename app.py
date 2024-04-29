"""
Web-app
"""

import json
import pymongo
from bson.objectid import ObjectId
from bson import json_util
from flask import Flask, render_template, session
from dotenv import dotenv_values
from nested_collections import NestedCollection
from setup_mg import end_mgd, start_mgd

config = dotenv_values(".env")


async def connect_to_mongo(app):
    """
    Connects to mongoDB asyncronously
    """

    mongo_uri = (
        f'mongodb://{config["MONGODB_USER"]}:'
        f'{config["MONGODB_PASSWORD"]}@{config["MONGODB_HOST"]}:'
        f'{config["MONGODB_PORT"]}?authSource={config["MONGODB_AUTHSOURCE"]}'
    )

    # Make a connection to the database server
    connection = pymongo.MongoClient(mongo_uri)

    try:
        # verify the connection works by pinging the database
        connection.admin.command(
            "ping"
        )  # The ping command is cheap and does not require auth.
        print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
    except pymongo.errors.OperationFailure as e:
        # the ping command failed, so the connection is not available.
        print(" * MongoDB connection error:", e)  # debug

    # Select a specific database on the server
    db = connection[config["MONGODB_NAME"]]

    print(db.test_collection.find_one({}))

    if not db.nested_collections.find_one({"name": "SE_Project5"}):
        db.nested_collections.insert_one({"name": "SE_Project5", "children": []})
    se5_db = NestedCollection("SE_Project5", db)

    start_mgd(se5_db)
    end_mgd(db, se5_db)
    if not db.nested_collections.find_one({"name": "SE_Project5"}):
        db.nested_collections.insert_one({"name": "SE_Project5", "children": []})
    se5_db = NestedCollection("SE_Project5", db)
    se5_db = NestedCollection("SE_Project5", db)
    start_mgd(se5_db)

    app.connected = True
    app.db = db


def create_app():
    """
    returns a flask app
    """
    # Make flask app
    app = Flask(__name__)
    app.secret_key = config["WEBAPP_FLASK_SECRET_KEY"]

    app.connected = False

    app.ensure_sync(connect_to_mongo)(app)

    @app.route("/")
    def home():
        """
        shows home page
        """
        if not session.get("associated_id"):
            session["associated_id"] = json.loads(json_util.dumps(ObjectId()))
            print(session["associated_id"].get("$oid"))
            print("Generating new session id")

        return render_template("home.html", home=True)

    @app.route("/play")
    def play():
        """
        shows play page
        """
        return render_template("play.html", play=True)
    
    return app
    



if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(port=config["WEBAPP_FLASK_PORT"])

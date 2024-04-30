"""
Web-app
"""

import json
import pymongo
from bson.objectid import ObjectId
from bson import json_util
from flask import Flask, render_template, session, request
from dotenv import dotenv_values
from nested_collections import NestedCollection
from setup_mg import end_mgd, start_mgd
from flask_socketio import SocketIO, emit

config = dotenv_values(".env")

## create a socketio object
socketio = SocketIO()

## use the word apple for guessing temporarily
curr_word = "apple"


async def connect_to_mongo(app):
    """
    Connects to mongoDB asyncronously..
    """
    mongo_uri = (
        f'mongodb+srv://{config["MONGODB_USER"]}:'
        f'{config["MONGODB_PASSWORD"]}@{config["MONGODB_HOST"]}'
        f'/{config["MONGODB_NAME"]}?retryWrites=true&w=majority&appName={config["MONGODB_NAME"]}'
    )

    # Make a connection to the database server
    connection = pymongo.MongoClient(mongo_uri)

    try:
        # verify the connection works by pinging the database
        connection.admin.command(
            "ping"
        )  # The ping command is cheap and does not require auth.
        print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
        app.connected = True
    except pymongo.errors.OperationFailure as err:
        # the ping command failed, so the connection is not available.
        print(" * MongoDB connection error:", err)  # debug
        app.connected = False
        return None

    # Select a specific database on the server
    dbase = connection[config["MONGODB_NAME"]]

    if not dbase.nested_collections.find_one({"name": "SE_Project5"}):
        dbase.nested_collections.insert_one({"name": "SE_Project5", "children": []})
    se5_db = NestedCollection("SE_Project5", dbase)

    start_mgd(se5_db)
    end_mgd(dbase, se5_db)
    if not dbase.nested_collections.find_one({"name": "SE_Project5"}):
        dbase.nested_collections.insert_one({"name": "SE_Project5", "children": []})

    se5_db = NestedCollection("SE_Project5", dbase)
    start_mgd(se5_db)

    app.db = dbase
    app.se5_db = se5_db


def create_app():
    """
    returns a flask app
    """
    # Make flask app
    app = Flask(__name__)
    app.secret_key = config["WEBAPP_FLASK_SECRET_KEY"]

    # attach socketio to the app
    socketio.init_app(app)

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

    @socketio.on("connect")
    def handle_connect():
        print("Client connected")

    @socketio.on("drawing")
    def handle_drawing(data):
        """
        Handles drawing data
        """
        print(data)
        # broadcast the drawing data, to all clients
        emit("drawing", data, broadcast=True, include_self=False)

    @socketio.on("canvas_cleared")
    def handle_clear():
        """
        Handles clearing the canvas
        """
        print("Clearing canvas")
        emit("canvas_cleared", broadcast=True)

    @socketio.on("disconnect")
    def handle_disconnect():
        print("Client disconnected")

    @socketio.on("submit_guess")
    def handle_guess(data):
        """
        Handles the guess
        """
        guess = data["guess"].lower().strip()
        is_correct = guess == curr_word

        if is_correct:
            response_message = "Correct!"
        else:
            response_message = "Incorrect!"

        emit(
            "guess",
            {"message": response_message, "is_correct": is_correct},
            room=request.sid,
        )

    return app

    @app.route("/test")
    def testing():
        """Shows testing page"""
        if not session.get("Associated_id"):
            session["associated_id"] = json.loads(json_util.dumps(ObjectId()))


if __name__ == "__main__":
    flask_app = create_app()
    socketio.run(
        flask_app, host="0.0.0.0", port=config["WEBAPP_FLASK_PORT"], debug=True
    )

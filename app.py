"""
Web-app
"""

import json
import pymongo
from flask_socketio import SocketIO, emit, join_room
from bson import json_util, objectid
from flask import Flask, render_template, session, request, redirect, url_for
from dotenv import dotenv_values
from nested_collections import NestedCollection
from setup_mg import end_mgd, start_mgd

config = dotenv_values(".env")

## create a socketio object
socketio = SocketIO()

## use the word apple for guessing temporarily
curr_word = "apple"

ROOM_SIZE = 2


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

    app.rooms = {}

    @app.route("/")
    def home():
        """
        shows home page
        """
        if not session.get("associated_id"):
            session["associated_id"] = json.loads(json_util.dumps(objectid.ObjectId()))
            print(session["associated_id"].get("$oid"))
            print("Generating new session id")

        return render_template("home.html", home=True)

    @app.route("/play")
    def play():
        """
        shows play page
        """
        return render_template("play.html", play=True)

    @app.route("/join-game", methods=["GET", "POST"])
    def join_game():
        """Page with all possible rooms"""

        if request.args.get("room"):
            session["room"] = request.args.get("room")
            return redirect(url_for("waiting_room"))

        full_rooms = app.se5_db["rooms"].find({"count": ROOM_SIZE})
        free_rooms = app.se5_db["rooms"].find({"count": {"$lt": ROOM_SIZE}})

        if request.method == "GET":
            return render_template(
                "join-game.html", full_rooms=full_rooms, free_rooms=free_rooms
            )

        if request.method == "POST":
            if app.se5_db["rooms"].find_one({"name": request.form["room"]}):
                print("already exists")
                return redirect(
                    url_for(
                        "join_game",
                        full_rooms=full_rooms,
                        free_rooms=free_rooms,
                        error="room already exists",
                    )
                )
            session["room"] = request.form["room"]
            app.se5_db["rooms"].insert_one({"name": request.form["room"], "count": 0})
            return redirect(url_for("waiting_room"))

        return redirect(
            url_for(
                "join_game",
                full_rooms=full_rooms,
                free_rooms=free_rooms,
                error="Unexpected error",
            )
        )

    @app.route("/waiting-room")
    def waiting_room():
        """Waiting room page"""
        return render_template("waiting.html", room=session["room"])

    @socketio.on("connect", namespace="/waiting")
    def handle_waiting_connect():
        """Send socket event ready when waiting room full"""
        room = session["room"]

        app.se5_db: NestedCollection = app.se5_db  # type: ignore
        app.se5_db["rooms"].update_one(
            {"name": room}, {"$inc": {"count": 1}, "$set": {"name": room}}
        )

        emit("assigned-room", {"room": room}, broadcast=False, namespace="/waiting")
        if app.se5_db["rooms"].find_one({"name": room})["count"] == ROOM_SIZE:
            print(f"sufficient people... ready to start room {room}")
            emit(
                "ready",
                {"message": f"{room} is ready", "room": room},
                broadcast=True,
                namespace="/waiting",
            )

    @socketio.on("connect", namespace="/play")
    def handle_connect():
        print("Client connected")
        username = session["associated_id"]
        room = session["room"]
        join_room(room)
        print(username, "joined", room)
        emit(
            "new-player",
            {"message": f"{username} joined {room}"},
            broadcast=True,
            namespace="/play",
            to=room,
        )

    @socketio.on("drawing", namespace="/play")
    def handle_drawing(data):
        """
        Handles drawing data
        """
        # print(data)
        # broadcast the drawing data, to all clients
        emit(
            "drawing",
            data,
            broadcast=True,
            include_self=False,
            namespace="/play",
            to=session["room"],
        )

    @socketio.on("canvas_cleared", namespace="/play")
    def handle_clear():
        """
        Handles clearing the canvas
        """
        print("Clearing canvas")
        emit("canvas_cleared", broadcast=True, namespace="/play", to=session["room"])

    @socketio.on("disconnect", namespace="/play")
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


if __name__ == "__main__":
    flask_app = create_app()
    socketio.run(
        flask_app, host="0.0.0.0", port=config["WEBAPP_FLASK_PORT"], debug=True
    )

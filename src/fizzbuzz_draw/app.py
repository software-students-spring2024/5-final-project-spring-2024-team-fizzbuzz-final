"""
Web-app
"""

import json
import random
import pymongo
from flask_socketio import SocketIO, emit, join_room
from bson import json_util, objectid
from flask import Flask, render_template, session, request, redirect, url_for
from dotenv import dotenv_values
from src.fizzbuzz_draw.nested_collections import NestedCollection
from src.fizzbuzz_draw.setup_mg import end_mgd, start_mgd

config = dotenv_values(".env")

## create a socketio object
socketio = SocketIO()

ROOM_SIZE = 3


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


def create_app():  # pylint: disable=too-many-statements
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
            session["associated_id"] = json.loads(json_util.dumps(objectid.ObjectId()))
            print("Generating new session id")

        return redirect(url_for("join_game"))

    @app.route("/scores")
    def scores():
        """
        shows scores page
        """

        scores_raw = app.se5_db["scores"].find(
            {"player": objectid.ObjectId(session["associated_id"]["$oid"])}
        )
        scores = list(scores_raw)

        return render_template("scores.html", scores=scores, foundAny=len(scores) > 0)

    @app.route("/play")
    def play():
        """
        shows play page
        """

        db_room = app.se5_db["rooms"].find_one({"name": session["room"]})

        return render_template(
            "play.html",
            play=True,
            guess=session["associated_id"]["$oid"] != db_room["draw"]["$oid"],
        )

    @app.route("/join-game", methods=["GET", "POST"])
    def join_game():
        """Page with all possible rooms"""

        if request.args.get("room"):
            session["room"] = request.args.get("room")
            return redirect(url_for("waiting_room"))

        full_rooms = app.se5_db["rooms"].find({"count": ROOM_SIZE})
        free_rooms = app.se5_db["rooms"].find({"count": {"$lt": ROOM_SIZE}})
        theme_packs = app.se5_db["theme_packs"].find()

        if request.method == "GET":
            return render_template(
                "join-game.html",
                full_rooms=full_rooms,
                free_rooms=free_rooms,
                theme_packs=theme_packs,
                error="",
            )

        if request.method == "POST":
            if app.se5_db["rooms"].find_one({"name": request.form["room"]}):
                print("already exists")
                return redirect(
                    url_for(
                        "join_game",
                        full_rooms=full_rooms,
                        free_rooms=free_rooms,
                        theme_packs=theme_packs,
                        error="room already exists",
                    )
                )
            session["room"] = request.form["room"]
            app.se5_db["rooms"].insert_one(
                {
                    "name": request.form["room"],
                    "count": 0,
                    "players": [],
                    "draw": None,
                    "theme_pack": request.form["theme_pack"],
                    "num_rounds": 3,
                }
            )
            return redirect(url_for("waiting_room"))

        return redirect(
            url_for(
                "join_game",
                full_rooms=full_rooms,
                free_rooms=free_rooms,
                theme_packs=theme_packs,
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
            {"name": room},
            {"$inc": {"count": 1}, "$push": {"players": session["associated_id"]}},
        )

        join_room(room)
        db_room = app.se5_db["rooms"].find_one({"name": room})
        if db_room["count"] == ROOM_SIZE:
            rand_ind = random.randint(1, ROOM_SIZE - 1)
            draw = db_room["players"][rand_ind]
            app.se5_db["rooms"].update_one({"name": room}, {"$set": {"draw": draw}})
            print(f"sufficient people... ready to start room {room}")
            emit(
                "ready",
                {"message": f"{room} is ready", "room": room, "draw": draw},
                broadcast=True,
                namespace="/waiting",
                to=room,
            )

    @socketio.on("connect", namespace="/play")
    def handle_connect():
        print("Client connected")
        username = session["associated_id"]
        room = session["room"]
        db_room = app.se5_db["rooms"].find_one({"name": room})

        theme_pack = app.se5_db["theme_packs"].find_one(
            {"theme": db_room["theme_pack"]}
        )

        rand_ind = random.randint(0, len(theme_pack["prompts"]) - 1)
        word = theme_pack["prompts"][rand_ind]

        join_room(room)
        print(username, "joined", room)
        emit(
            "new-player",
            {
                "message": f"{username} joined {room}",
            },
            broadcast=True,
            include_self=False,
            namespace="/play",
            to=room,
        )
        emit(
            "joined",
            {
                "draw": db_room["draw"]["$oid"] == session["associated_id"]["$oid"],
            },
            broadcast=False,
        )
        emit(
            "prompt",
            {"word": word},
            broadcast=True,
            include_self=True,
            namespace="/play",
            to=room,
        )

    @socketio.on("drawing", namespace="/play")
    def handle_drawing(data):
        """
        Handles drawing data
        """
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

    @socketio.on("guessed", namespace="/play")
    def handle_guess(data):
        """
        Handles the guess
        """
        print("ENTERED!")
        db_room = app.se5_db["rooms"].find_one({"name": session["room"]})

        db_score = app.se5_db["scores"].find_one(
            {
                "player": objectid.ObjectId(session["associated_id"]["$oid"]),
                "game": session["room"],
            }
        )

        if not db_score:
            app.se5_db["scores"].insert_one(
                {
                    "player": objectid.ObjectId(session["associated_id"]["$oid"]),
                    "game": session["room"],
                    "score": 0,
                    "num_rounds": db_room["num_rounds"],
                }
            )

        if not data["skipped"]:
            app.se5_db["scores"].update_one(
                {
                    "player": objectid.ObjectId(session["associated_id"]["$oid"]),
                    "game": session["room"],
                },
                {"$inc": {"score": 1}},
            )

        print(db_room["count"])

        if db_room["count"] > 2:
            app.se5_db["rooms"].update_one(
                {"name": session["room"]},
                {"$inc": {"count": -1}, "$push": {"players": session["associated_id"]}},
            )
        else:
            if db_room["num_rounds"] == 1:
                print("done")
                app.se5_db["rooms"].delete_one({"name": session["room"]})
                emit(
                    "scores",
                    {},
                    broadcast=True,
                    include_self=True,
                    namespace="/play",
                    to=session["room"],
                )

                return

            app.se5_db["rooms"].update_one(
                {"name": session["room"]},
                {
                    "$set": {"count": ROOM_SIZE},
                    "$push": {
                        "players": objectid.ObjectId(session["associated_id"]["$oid"])
                    },
                    "$inc": {"num_rounds": -1},
                },
            )

            rand_ind = random.randint(1, ROOM_SIZE - 1)
            draw = db_room["players"][rand_ind]
            print(draw)
            app.se5_db["rooms"].update_one(
                {"name": session["room"]}, {"$set": {"draw": draw}}
            )

            emit(
                "next-round",
                {},
                broadcast=True,
                include_self=True,
                namespace="/play",
                to=session["room"],
            )

    return app


def main():
    """Main"""
    flask_app = create_app()
    socketio.run(flask_app, host="0.0.0.0", port=config["WEBAPP_FLASK_PORT"])
    # return flask_app


if __name__ == "__main__":
    main()

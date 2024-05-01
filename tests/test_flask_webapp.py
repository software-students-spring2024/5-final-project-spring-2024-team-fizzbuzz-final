"""
    Tests for functions used in the webapp
"""

import pytest
from flask_socketio import SocketIOTestClient
from fizzbuzz_draw.app import create_app, end_mgd, socketio


class Tests:
    """
    Class for handling tests
    """

    @pytest.fixture
    def app_c(self):
        """
        Creates an app (synchronously connect to mongodb).
        """

        app = create_app()

        app.config.update(
            {
                "TESTING": True,
            }
        )

        assert app is not None
        assert app.connected

        # other setup can go here

        yield app

        # clean up / reset resources here
        if not hasattr(app, "db"):
            app.db = None
        if not hasattr(app, "se5_db"):
            app.se5_db = None
        end_mgd(app.db, app.se5_db)

        self.stupid()

    def stupid(self):
        """most intelligent function"""
        print(self, "Hola")

    def test_mongo(self, app_c):
        """test that mongodb is connected to"""
        assert app_c.db is not None
        assert app_c.se5_db is not None

        test = app_c.se5_db["theme_packs"].find_one({})

        assert test is not None

        self.stupid()

    def test_join_game(self, app_c):
        """checking whether user trying to join game gets redirected to html page"""
        self.stupid()
        user1 = app_c.test_client()

        response = user1.get("/join-game")
        assert 200 <= response.status_code < 300

    @pytest.fixture
    def app_with_room(self, app_c):
        """checking whether user who creates room gets redirected"""
        self.stupid()
        user1 = app_c.test_client()

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        response = user1.post("/join-game", data=data)
        assert 300 <= response.status_code < 400

        yield (app_c, user1)

    def test_score(self, app_c):
        """testing scores page"""
        user1 = app_c.test_client()

        user1.get("/")
        response = user1.get("/scores")

        assert 200 <= response.status_code < 300

    def test_socket_io_join_game(self, app_with_room):
        """checking whether second user to join created room gets redirected"""
        self.stupid()

        app_c = app_with_room[0]

        user2 = app_c.test_client()
        response2 = user2.get("/join-game?room=firfir")
        assert 300 <= response2.status_code < 400

    def test_socket_rejected(self, app_c):
        """make sure server rejected the connection"""
        self.stupid()

        user = app_c.test_client()

        # Create a SocketIO instance
        socketio_test_client = SocketIOTestClient(
            app=app_c, flask_test_client=user, socketio=socketio
        )

        # make sure the server rejected the connection
        assert socketio_test_client.is_connected()

    def test_session_associated_id(self, app_c):
        """make sure the user received an associated_id"""
        self.stupid()

        user = app_c.test_client()
        user.get("/")

        with user.session_transaction() as sess:
            assert sess["associated_id"] is not None

    def test_session_room(self, app_with_room):
        """make sure the user joins the right room"""
        self.stupid()

        app_c = app_with_room[0]
        user1 = app_with_room[1]

        user2 = app_c.test_client()

        user2.get("/join-game?room=firfir")

        user1.get("/waiting-room")
        user2.get("/waiting-room")

        with user2.session_transaction() as sess:
            assert sess["room"] == "firfir"

    def test_socket_to_join_waiting_namespace(self, app_c):
        """checking whether user to join created game is connected to right namespace"""
        self.stupid()

        user1 = app_c.test_client()
        user2 = app_c.test_client()
        # user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        user2.get("/waiting-room")

        socketio_test_client = socketio.test_client(
            app=app_c, namespace="/waiting", flask_test_client=user2
        )
        # response3 = user3.get("/join-game?room="+data["room"])
        assert socketio_test_client.is_connected(namespace="/waiting")

    def test_join_game_load_html(self, app_c):
        """checking whether user loads html when sent to game"""
        self.stupid()

        user1 = app_c.test_client()
        user2 = app_c.test_client()
        user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")
        user3.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])
        user3.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user1)

        user2.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user2)

        user3.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user3)

        user1.get("/play")
        user2.get("/play")
        user3.get("/play")
        response = user3.get("/play")

        assert 200 <= response.status_code < 300

    def test_whether_user_in_play_is_connected(self, app_c):
        """checking whether user to join created game is connected to right namespace"""
        self.stupid()

        user1 = app_c.test_client()
        user2 = app_c.test_client()
        user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")
        user3.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])
        user3.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/waiting", flask_test_client=user1
        )

        user2.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user2)

        user3.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user3)

        user1.get("/play")
        user2.get("/play")
        user3.get("/play")

        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/play", flask_test_client=user1
        )

        assert socketio_test_client1.is_connected(namespace="/play")

    def test_whether_user_in_play_has_right_room(self, app_c):
        """checking whether user to join created game is connected to right namespace"""
        self.stupid()

        user1 = app_c.test_client()
        user2 = app_c.test_client()
        user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")
        user3.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])
        user3.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user1)

        user2.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user2)

        user3.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user3)

        user1.get("/play")
        user2.get("/play")
        user3.get("/play")

        socketio.test_client(app=app_c, namespace="/play", flask_test_client=user1)

        with user1.session_transaction() as sess:
            assert sess["room"] == "firfir"

    def test_canvas_clear(self, app_c):
        """checking canvas clear"""
        user1 = app_c.test_client()
        user2 = app_c.test_client()
        user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")
        user3.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])
        user3.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/waiting", flask_test_client=user1
        )

        user2.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user2)

        user3.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user3)

        user1.get("/play")
        user2.get("/play")
        user3.get("/play")

        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/play", flask_test_client=user1
        )
        socketio.test_client(app=app_c, namespace="/play", flask_test_client=user2)
        socketio.test_client(app=app_c, namespace="/play", flask_test_client=user3)

        socketio_test_client1.emit("canvas_cleared", namespace="/play")

        lst = socketio_test_client1.get_received(namespace="/play")

        assert lst[-1]["name"] == "canvas_cleared"

    def test_drawing(self, app_c):
        """checking drawing"""
        user1 = app_c.test_client()
        user2 = app_c.test_client()
        user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")
        user3.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])
        user3.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/waiting", flask_test_client=user1
        )

        user2.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user2)

        user3.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user3)

        user1.get("/play")
        user2.get("/play")
        user3.get("/play")

        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/play", flask_test_client=user1
        )
        socketio.test_client(app=app_c, namespace="/play", flask_test_client=user2)
        socketio.test_client(app=app_c, namespace="/play", flask_test_client=user3)

        socketio_test_client1.emit("drawing", {}, namespace="/play")

        lst = socketio_test_client1.get_received(namespace="/play")

        assert lst[-1]["name"] == "prompt"

    def test_guess(self, app_c):
        """testing"""
        user1 = app_c.test_client()
        user2 = app_c.test_client()
        user3 = app_c.test_client()
        user1.get("/")
        user2.get("/")
        user3.get("/")

        data = {}
        data["room"] = "firfir"
        data["theme_pack"] = "fruits"
        user1.post("/join-game", data=data)
        user2.get("/join-game?room=" + data["room"])
        user3.get("/join-game?room=" + data["room"])

        user1.get("/waiting-room")
        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/waiting", flask_test_client=user1
        )

        user2.get("/waiting-room")
        socketio_test_client2 = socketio.test_client(
            app=app_c, namespace="/waiting", flask_test_client=user2
        )

        user3.get("/waiting-room")
        socketio.test_client(app=app_c, namespace="/waiting", flask_test_client=user3)

        user1.get("/play")
        user2.get("/play")
        user3.get("/play")

        socketio_test_client1 = socketio.test_client(
            app=app_c, namespace="/play", flask_test_client=user1
        )
        socketio_test_client2 = socketio.test_client(
            app=app_c, namespace="/play", flask_test_client=user2
        )
        socketio.test_client(app=app_c, namespace="/play", flask_test_client=user3)

        for _ in range(2):
            socketio_test_client1.emit("guessed", {"skipped": False}, namespace="/play")
            socketio_test_client2.emit("guessed", {"skipped": False}, namespace="/play")
            lst_i = socketio_test_client1.get_received(namespace="/play")
            print(lst_i)
            assert lst_i[-1]["name"] == "next-round"

            user1.get("/play")
            user2.get("/play")
            user3.get("/play")
            socketio_test_client1 = socketio.test_client(
                app=app_c, namespace="/play", flask_test_client=user1
            )
            socketio_test_client2 = socketio.test_client(
                app=app_c, namespace="/play", flask_test_client=user2
            )
            socketio.test_client(app=app_c, namespace="/play", flask_test_client=user3)

        socketio_test_client1.emit("guessed", {"skipped": False}, namespace="/play")
        socketio_test_client2.emit("guessed", {"skipped": False}, namespace="/play")
        lst_i = socketio_test_client1.get_received(namespace="/play")
        print(lst_i)
        assert lst_i[-1]["name"] == "scores"

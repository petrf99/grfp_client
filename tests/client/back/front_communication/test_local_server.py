import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from client.back.front_communication.local_server import back_app, client_state, message_queue


@pytest.fixture
def client():
    """Flask test client fixture."""
    back_app.config["TESTING"] = True
    with back_app.test_client() as client:
        yield client


# === /shutdown ===
@patch("client.back.front_communication.local_server.back_server", new=MagicMock())
@patch("tech_utils.flask_server_utils.shutdown_server", return_value=True)
def test_shutdown_success(mock_shutdown, client):
    """Should trigger server shutdown and return success."""
    client_state.stop_back_event.clear()

    response = client.post("/shutdown")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert client_state.stop_back_event.is_set()


@patch("client.back.front_communication.local_server.back_server", new=MagicMock())
@patch("tech_utils.flask_server_utils.shutdown_server", return_value=False)
@patch("client.back.front_communication.local_server.send_message_to_front")
def test_shutdown_failure(mock_send, mock_shutdown, client):
    """Should log error and call send_message_to_front if shutdown fails."""
    response = client.post("/shutdown")
    assert response.status_code == 200
    mock_send.assert_called_once()


# === /front-connect ===

@patch("client.back.front_communication.local_server.connect")
def test_front_connect_success(mock_connect, client):
    """Should start connect thread and return ok."""
    response = client.post("/front-connect", json={"mission_id": "abc"})
    assert response.status_code == 200
    mock_connect.assert_called_once_with("abc")


def test_front_connect_missing_mission_id(client):
    """Should return 400 if mission_id is missing."""
    response = client.post("/front-connect", json={})
    assert response.status_code == 400


# === /front-disconnect ===

@patch("client.back.front_communication.local_server.disconnect")
def test_front_disconnect_starts_thread(mock_disconnect, client):
    """Should start disconnect thread and return ok."""
    response = client.post("/front-disconnect")
    assert response.status_code == 200
    mock_disconnect.assert_called_once()


# === /front-launch-session ===

@patch("client.back.front_communication.local_server.start_session")
def test_front_launch_session_success(mock_start, client):
    """Should trigger session start if session_id is set."""
    client_state.session_id = "abc"
    response = client.post("/front-launch-session")
    assert response.status_code == 200
    client_state.session_id = None


def test_front_launch_session_without_session(client):
    """Should return 400 if no session_id is present."""
    client_state.session_id = None
    response = client.post("/front-launch-session")
    assert response.status_code == 400


# === /front-close-session ===

@patch("client.back.front_communication.local_server.local_close_sess")
def test_front_close_session_finish(mock_close, client):
    """Should handle valid 'finish' result and start thread."""
    client_state.session_id = "xyz"
    client_state.finish_event.clear()

    response = client.post("/front-close-session", json={"result": "finish"})
    assert response.status_code == 200
    assert client_state.finish_event.is_set()
    client_state.session_id = None


@patch("client.back.front_communication.local_server.local_close_sess")
def test_front_close_session_abort(mock_close, client):
    """Should handle valid 'abort' result and set abort_event."""
    client_state.session_id = "xyz"
    client_state.abort_event.clear()

    response = client.post("/front-close-session", json={"result": "abort"})
    assert response.status_code == 200
    assert client_state.abort_event.is_set()
    client_state.session_id = None


def test_front_close_session_invalid_result(client):
    """Should return 400 if result is invalid."""
    client_state.session_id = "xyz"
    response = client.post("/front-close-session", json={"result": "invalid"})
    assert response.status_code == 400
    client_state.session_id = None


def test_front_close_session_no_session(client):
    """Should return 400 if session_id is missing."""
    client_state.session_id = None
    response = client.post("/front-close-session", json={"result": "abort"})
    assert response.status_code == 400


# === /get-message ===

def test_get_message_success(client):
    """Should return next message from queue."""
    message_queue.clear()
    message_queue.append("ready to fly")

    response = client.post("/get-message")
    assert response.status_code == 200
    assert response.get_json()["message"] == "ready to fly"


def test_get_message_empty(client):
    """Should return error if queue is empty."""
    message_queue.clear()
    response = client.post("/get-message")
    assert response.status_code == 400

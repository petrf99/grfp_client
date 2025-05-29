import pytest
from unittest.mock import patch, MagicMock
from flask import json

# Fixtures for the Flask app and client
@pytest.fixture
def app():
    from client.back.gcs_communication import tcp_communication
    tcp_communication.app.config.update({"TESTING": True})
    yield tcp_communication.app

@pytest.fixture
def client(app):
    return app.test_client()

# === Tests for /shutdown ===

def test_shutdown_success(client):
    with patch("client.back.gcs_communication.tcp_communication.server", new=MagicMock()):
        response = client.post("/shutdown")
        assert response.status_code == 200
        assert b"Server shutting down" in response.data

def test_shutdown_not_running(client):
    from client.back.gcs_communication import tcp_communication
    tcp_communication.server = None
    response = client.post("/shutdown")
    assert response.status_code == 400
    assert b"Server not running" in response.data

# === Tests for /send-message ===

@patch("client.back.gcs_communication.tcp_communication.send_message_to_front")
def test_receive_abort_session(mock_send, client):
    response = client.post("/send-message", json={"message": "abort-session"})
    assert response.status_code == 200
    mock_send.assert_called_with("abort")

@patch("client.back.gcs_communication.tcp_communication.send_message_to_front")
def test_receive_finish_session(mock_send, client):
    response = client.post("/send-message", json={"message": "finish-session"})
    assert response.status_code == 200
    mock_send.assert_called_with("finish")

@patch("client.back.gcs_communication.tcp_communication.send_message_to_front")
def test_receive_start_session(mock_send, client):
    response = client.post("/send-message", json={
        "message": "start-session",
        "session_id": "abc123",
        "gcs_rc_port": 9001
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"
    mock_send.assert_called_once()

def test_receive_ping_status(client):
    response = client.post("/send-message", json={"message": "session-update"})
    assert response.status_code == 200
    assert json.loads(response.data)["status"] == "ok"

def test_receive_unknown_message(client):
    response = client.post("/send-message", json={"message": "unknown-command"})
    assert response.status_code == 400
    assert json.loads(response.data)["reason"] == "What?"

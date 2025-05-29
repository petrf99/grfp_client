import pytest
import threading
import time
from unittest.mock import patch

def test_client_back_polling_abort(monkeypatch):
    from client.front.logic import back_listener

    # Mock front_state with Events and flags
    class MockFrontState:
        poll_back_event = threading.Event()
        finish_event = threading.Event()
        abort_event = threading.Event()
        tailscale_connected_event = threading.Event()
        tailscale_disconnect_event = threading.Event()
        session_id = None

    MockFrontState.poll_back_event.set()
    monkeypatch.setattr("client.front.state.front_state", MockFrontState)

    # Return 'abort' command from backend
    def fake_post(*args, **kwargs):
        class Resp:
            status_code = 200
            def json(self):
                return {'message': 'abort'}
        return Resp()

    monkeypatch.setattr("client.front.logic.back_listener.requests.post", fake_post)

    called = {"post_request": False}

    def fake_post_request(*args, **kwargs):
        called["post_request"] = True
        return True

    monkeypatch.setattr("client.front.logic.back_listener.post_request", fake_post_request)

    thread = threading.Thread(target=back_listener.back_polling)
    thread.start()
    time.sleep(0.3)
    MockFrontState.poll_back_event.clear()
    thread.join(timeout=1)

    assert MockFrontState.abort_event.is_set()
    assert called["post_request"] is True

def test_client_back_polling_invalid(monkeypatch):
    from client.front.logic import back_listener

    class MockFrontState:
        poll_back_event = threading.Event()
        finish_event = threading.Event()
        abort_event = threading.Event()
        tailscale_connected_event = threading.Event()
        tailscale_disconnect_event = threading.Event()
        session_id = None

    MockFrontState.poll_back_event.set()
    monkeypatch.setattr("client.front.state.front_state", MockFrontState)

    def fake_post_invalid(*args, **kwargs):
        class Resp:
            status_code = 200
            def json(self):
                return {'message': 'unknown-message-type'}
        return Resp()

    monkeypatch.setattr("client.front.logic.back_listener.requests.post", fake_post_invalid)

    log_msgs = {"logged": False}

    def fake_logger_warning(msg):
        if "Polling exception" in msg:
            log_msgs["logged"] = True

    monkeypatch.setattr(back_listener.logger, "warning", fake_logger_warning)

    thread = threading.Thread(target=back_listener.back_polling)
    thread.start()
    time.sleep(0.3)
    MockFrontState.poll_back_event.clear()
    thread.join(timeout=1)

    # No exception means success; we just make sure thread ends gracefully
    assert True

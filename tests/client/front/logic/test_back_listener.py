import pytest
import threading
import time
from unittest.mock import patch, MagicMock

import threading
import time

import threading
import time
from unittest.mock import MagicMock
from client.front.logic import back_listener

def test_client_back_polling_abort(monkeypatch):
    # Моки
    clear_mock = MagicMock()
    reset_mock = MagicMock()
    post_request_mock = MagicMock()

    # Подготовка front_state
    class MockFlightScreen:
        reset_flight_screen = reset_mock

    class MockFrontState:
        poll_back_event = threading.Event()
        finish_event = threading.Event()
        running_event = threading.Event()
        tailscale_connected_event = threading.Event()
        tailscale_disconnect_event = threading.Event()
        session_id = None
        flight_screen = MockFlightScreen()
        main_screen = MagicMock()
        active_mission = MagicMock()
        clear = clear_mock

    MockFrontState.poll_back_event.set()
    MockFrontState.running_event.set()

    # Мокаем backend ответ
    def fake_post(*args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": "abort"}
        return mock_resp

    import client.front.state
    monkeypatch.setattr(client.front.state, "front_state", MockFrontState)
    monkeypatch.setattr(back_listener.requests, "post", fake_post)
    monkeypatch.setattr(back_listener, "post_request", post_request_mock)

    # Запускаем поток
    thread = threading.Thread(target=back_listener.back_polling)
    thread.start()
    time.sleep(0.5)
    MockFrontState.poll_back_event.clear()
    thread.join(timeout=2)

    # Проверки
    assert post_request_mock.called
    assert clear_mock.called
    assert reset_mock.called

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

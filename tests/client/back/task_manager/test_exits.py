import pytest
from unittest.mock import patch, MagicMock
from client.back.task_manager.exits import local_close_sess, disconnect
from client.back.state import client_state
from client.back.config import RSA_PRIVATE_PEM_PATH

@patch("client.back.task_manager.exits.send_message_to_front")
@patch("client.back.task_manager.exits.requests.post")
@patch("client.back.task_manager.exits.logger")
def test_local_close_sess_finish(mock_logger, mock_post, mock_send_msg):
    client_state.gcs_ip = "127.0.0.1"
    client_state.session_id = "session-1"
    client_state.external_stop_event.clear()
    client_state.token = "dummy_token"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    with patch("client.back.task_manager.exits.delete_vpn_connection") as mock_delete:
        with patch.object(client_state, 'clear') as mock_clear:
            result = local_close_sess(finish_flg=True)
            assert result is True
            mock_post.assert_called()
            mock_delete.assert_called_once()
            mock_clear.assert_called_once()
            mock_send_msg.assert_any_call("Session closed")

@patch("client.back.task_manager.exits.send_message_to_front")
@patch("client.back.task_manager.exits.requests.post", side_effect=Exception("network error"))
@patch("client.back.task_manager.exits.logger")
def test_local_close_sess_post_exception(mock_logger, mock_post, mock_send_msg):
    client_state.gcs_ip = "127.0.0.1"
    client_state.session_id = "session-1"
    client_state.external_stop_event.clear()
    client_state.token = "token"

    with patch("client.back.task_manager.exits.delete_vpn_connection") as mock_delete:
        with patch.object(client_state, 'clear') as mock_clear:
            result = local_close_sess()
            assert result is True
            mock_post.assert_called()
            mock_send_msg.assert_any_call("Something went wrong. Terminating session forcibly...")
            mock_delete.assert_called_once()
            mock_clear.assert_called_once()

@patch("client.back.task_manager.exits.send_message_to_front")
@patch("client.back.task_manager.exits.logger")
@patch("client.back.task_manager.exits.tailscale_down")
def test_disconnect_keys_deleted(mock_ts_down, mock_logger, mock_send_msg):
    with patch("os.path.exists", return_value=True), \
         patch("os.remove") as mock_remove:
        result = disconnect()
        assert result is True
        mock_ts_down.assert_called_once()
        assert mock_remove.call_count == 2
        mock_logger.info.assert_any_call(f"Private key {RSA_PRIVATE_PEM_PATH} deleted.")

@patch("client.back.task_manager.exits.send_message_to_front")
@patch("client.back.task_manager.exits.logger")
@patch("client.back.task_manager.exits.tailscale_down")
def test_disconnect_keys_not_found(mock_ts_down, mock_logger, mock_send_msg):
    with patch("os.path.exists", return_value=False), \
         patch("os.remove") as mock_remove:
        result = disconnect()
        assert result is True
        mock_ts_down.assert_called_once()
        mock_remove.assert_not_called()
        mock_logger.warning.assert_any_call(f"Private key {RSA_PRIVATE_PEM_PATH} not found — nothing to delete.")

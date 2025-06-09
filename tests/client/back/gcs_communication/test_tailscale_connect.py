import base64
import pytest
from unittest.mock import patch, MagicMock, mock_open
from cryptography.hazmat.primitives.asymmetric import rsa
from client.back.gcs_communication import tailscale_connect
from client.back.state import client_state


# === Helper: Create fake RSA keypair ===
def generate_fake_rsa_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=tailscale_connect.serialization.Encoding.PEM,
        format=tailscale_connect.serialization.PrivateFormat.PKCS8,
        encryption_algorithm=tailscale_connect.serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=tailscale_connect.serialization.Encoding.PEM,
        format=tailscale_connect.serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, private_pem, public_pem


# === Test: connect() ===

@patch("client.back.gcs_communication.tailscale_connect.get_vpn_connection", return_value=False)
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_connect_failure(mock_send, mock_get):
    """Should send failure message if get_vpn_connection fails."""
    result = tailscale_connect.connect("mission123")
    assert result is False
    assert client_state.mission_id == "mission123"
    mock_send.assert_called_once()
    assert "ts-disconnected" in mock_send.call_args[0][0].lower()


@patch("client.back.gcs_communication.tailscale_connect.start_tailscale", return_value=True)
@patch("client.back.gcs_communication.tailscale_connect.get_vpn_connection", return_value=True)
def test_connect_success(mock_get, mock_start):
    """Should return True when both VPN retrieval and Tailscale start succeed."""
    assert tailscale_connect.connect("mission-abc")
    assert client_state.mission_id == "mission-abc"


# === Test: start_tailscale() ===

@patch("client.back.gcs_communication.tailscale_connect.tailscale_up", return_value=False)
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_start_tailscale_failure(mock_send, mock_up):
    """Should return False and notify front on Tailscale failure."""
    client_state.hostname = "test-host"
    client_state.token = "abc123"
    assert tailscale_connect.start_tailscale() is False
    mock_send.assert_called_once()
    assert "connect failed" in mock_send.call_args[0][0].lower()


@patch("client.back.gcs_communication.tailscale_connect.tailscale_up", return_value=True)
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_start_tailscale_success(mock_send, mock_up):
    """Should notify front on successful Tailscale connect."""
    client_state.hostname = "host1"
    client_state.token = "token1"
    assert tailscale_connect.start_tailscale() is True
    mock_send.assert_called_once_with("ts-connected ✅ Tailscale connected")


# === Test: get_vpn_connection() ===

@patch("client.back.gcs_communication.tailscale_connect.post_request")
@patch("client.back.gcs_communication.tailscale_connect.generate_keys_if_needed")
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_get_vpn_connection_success(mock_send, mock_gen_keys, mock_post):
    """Should decrypt token and update state when response is valid."""
    client_state.mission_id = "missionX"
    private_key, private_pem, public_pem = generate_fake_rsa_pair()

    # Prepare fake encrypted token
    encrypted_token = base64.b64encode(
        private_key.public_key().encrypt(
            b"vpn-token-123",
            tailscale_connect.padding.OAEP(
                mgf=tailscale_connect.padding.MGF1(algorithm=tailscale_connect.hashes.SHA256()),
                algorithm=tailscale_connect.hashes.SHA256(),
                label=None
            )
        )
    ).decode()

    # Mock post_request response
    mock_post.return_value = {
        "token": encrypted_token,
        "hostname": "test-client",
        "token_hash": "hash123"
    }

    with patch("builtins.open", mock_open(read_data=public_pem)) as m_pub:
        with patch("client.back.gcs_communication.tailscale_connect.open", mock_open(read_data=private_pem)):
            result = tailscale_connect.get_vpn_connection()

    assert result is True
    assert client_state.token == "vpn-token-123"
    assert client_state.hostname == "test-client"
    assert client_state.token_hash == "hash123"
    mock_send.assert_any_call("✅ VPN credentials obtained.")


@patch("client.back.gcs_communication.tailscale_connect.post_request", return_value=None)
@patch("client.back.gcs_communication.tailscale_connect.generate_keys_if_needed")
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_get_vpn_connection_failure(mock_send, mock_keys, mock_post):
    """Should notify failure and return False if post_request fails."""
    client_state.mission_id = "fail123"
    with patch("builtins.open", mock_open(read_data=b"...")):
        result = tailscale_connect.get_vpn_connection()

    assert result is False
    mock_send.assert_any_call("❌ Can't obtain VPN credentials. Please contact admin")


# === Test: delete_vpn_connection() ===

@patch("client.back.gcs_communication.tailscale_connect.post_request", return_value=True)
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_delete_vpn_connection_success(mock_send, mock_post):
    """Should notify success and return True when RFD responds OK."""
    client_state.hostname = "delete-host"
    client_state.token_hash = "abc123"
    assert tailscale_connect.delete_vpn_connection() is True
    mock_send.assert_called_with("✅ VPN credentials deleted from RFD.")


@patch("client.back.gcs_communication.tailscale_connect.post_request", return_value=None)
@patch("client.back.gcs_communication.tailscale_connect.send_message_to_front")
def test_delete_vpn_connection_failure(mock_send, mock_post):
    """Should notify failure and return False when RFD fails."""
    client_state.hostname = "delete-host"
    client_state.token_hash = "abc123"
    assert tailscale_connect.delete_vpn_connection() is False
    mock_send.assert_called_with("❌ Can't delete VPN credentials from RFD. Please contact admin")

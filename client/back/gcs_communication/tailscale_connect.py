from tech_utils.logger import init_logger

import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from tech_utils.cryptography import generate_keys_if_needed
from tech_utils.safe_post_req import post_request
from tech_utils.tailscale import tailscale_up

from client.back.config import (
    RFD_DOMAIN_NAME, RFD_CM, RSA_PRIVATE_PEM_PATH, RSA_PUBLIC_PEM_PATH
)
from client.back.state import client_state
from client.back.front_communication.front_msg_sender import send_message_to_front

logger = init_logger(name="Tailscale_Connect", component="back")

# === Constants ===
RFD_URL = f"https://{RFD_DOMAIN_NAME}/{RFD_CM}"
RFD_CONNECT_URL = f"{RFD_URL}/get-vpn-connection"
RFD_DELETE_CONN_URL = f"{RFD_URL}/delete-vpn-connection"

# === Internal ===

def connect(mission_id: str) -> bool:
    """
    Orchestrates the full connection to Tailscale via RFD.
    Stores mission_id and attempts to retrieve and activate VPN credentials.
    """
    client_state.mission_id = mission_id
    if not get_vpn_connection():
        send_message_to_front("ts-disconnected ❌ Tailscale connect failed")
        return False

    return start_tailscale()

def start_tailscale() -> bool:
    """
    Uses stored hostname and token to bring up the Tailscale connection.
    """
    if not tailscale_up(client_state.hostname, client_state.token):
        send_message_to_front("ts-disconnected ❌ Tailscale connect failed")
        return False
    
    send_message_to_front("ts-connected ✅ Tailscale connected")
    return True


# === RFD API ===

def get_vpn_connection() -> bool:
    """
    Sends a request to the RFD to retrieve VPN connection credentials using RSA public key encryption.
    Expects a base64-encoded token in response, which it decrypts with the private key.
    """
    send_message_to_front("Requesting VPN credentials from Remote Flights Dispatcher...")
    logger.info("Sending get-vpn-connection request to RFD")

    # Ensure RSA key pair exists
    logger.info("Generating RSA keys if needed")
    generate_keys_if_needed(RSA_PRIVATE_PEM_PATH, RSA_PUBLIC_PEM_PATH)

    # Load public key to send
    with open(RSA_PUBLIC_PEM_PATH, "rb") as f:
        public_pem = f.read()

    payload = {
        "tag": "client",
        "rsa_pub_key": public_pem.decode('utf-8'),
        "mission_id": client_state.mission_id
    }

    # Send request
    res = post_request(RFD_CONNECT_URL, payload, "Client get-vpn-connection")
    if res:
        # Decrypt and store token
        with open(RSA_PRIVATE_PEM_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        client_state.token = private_key.decrypt(
            base64.b64decode(res.get("token")),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        ).decode()

        # Save metadata
        client_state.hostname = res.get("hostname")
        client_state.token_hash = res.get("token_hash")

        send_message_to_front("✅ VPN credentials obtained.")
        logger.info(f"get-vpn-connection succeeded. Hostname: {client_state.hostname}, Token hash: {client_state.token_hash}, Token (last 10 chars): {client_state.token[-10:]}")
        return True
    else:
        send_message_to_front("❌ Can't obtain VPN credentials. Please contact admin")
        logger.error("get-vpn-connection failed.")
        return False
    

def delete_vpn_connection() -> bool:
    """
    Informs the RFD that this client's VPN credentials should be revoked.
    """
    send_message_to_front("Deleting VPN credentials from Remote Flights Dispatcher...")
    logger.info("Sending delete-vpn-connection request to RFD")

    payload = {
        "hostname": client_state.hostname,
        "token_hash": client_state.token_hash
    }

    res = post_request(RFD_DELETE_CONN_URL, payload, "Client delete-vpn-connection")
    if res:
        send_message_to_front("✅ VPN credentials deleted from RFD.")
        logger.info(f"delete-vpn-connection succeeded. Hostname: {client_state.hostname}, Token hash: {client_state.token_hash}")
    else:
        send_message_to_front("❌ Can't delete VPN credentials from RFD. Please contact admin")
        logger.error("delete-vpn-connection failed.")

    return res is not None



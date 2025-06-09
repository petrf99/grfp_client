import requests
import time
import os

from tech_utils.tailscale import tailscale_down
from client.back.config import GCS_TCP_PORT, ABORT_MSG, FINISH_MSG, RSA_PRIVATE_PEM_PATH, RSA_PUBLIC_PEM_PATH
from client.back.gcs_communication.tailscale_connect import delete_vpn_connection
from client.back.state import client_state
from client.back.front_communication.front_msg_sender import send_message_to_front

from tech_utils.logger import init_logger
logger = init_logger("Back_BasicCmds")

# Gracefully close a session, notify GCS, clean up state
def local_close_sess(finish_flg=False):
    send_message_to_front("Closing session...")
    logger.info("Closing session")
    status = ABORT_MSG
    if finish_flg:
        status = FINISH_MSG

    try:
        # If GCS has not externally closed the session, notify it
        if not client_state.external_stop_event.is_set():
            url = f"http://{client_state.gcs_ip}:{GCS_TCP_PORT}/send-message"
            payload = {
                "session_id": client_state.session_id,
                "message": f"{status}-session"
            }
            send_message_to_front(f"📡 Sending {status}-session to GCS at {client_state.gcs_ip}...")
            try:
                res = requests.post(url, json=payload, timeout=5)
                if res.status_code == 200:
                    send_message_to_front(f"Message {status}-session successfully sent to GCS.")
                    logger.info(f"{client_state} {status} message sent to GCS")
            except Exception as e:
                send_message_to_front("Something went wrong. Terminating session forcibly...")
                logger.error(f"{client_state} Failed to send {status} message to GCS. Exception: {e}. Forcing termination.")
    except Exception as e:
        logger.error(f"Unexpected error while sending {status}-session to GCS: {e}")

    # Disconnect from Tailnet
    if client_state.token:
        disconnect(True)

    # Clear session state
    client_state.clear()
    send_message_to_front("Session closed")
    logger.info(f"Session closed")

    return True


# Disconnect from Tailscale, delete local RSA keys
def disconnect(call_from_close_sess=False):
    # Close session if it is
    if not call_from_close_sess and client_state.session_id:
        local_close_sess()

    # Revoke VPN credentials if they exist
    if client_state.token:
        delete_vpn_connection()
        
    # Stop Tailscale network
    tailscale_down()
    send_message_to_front("ts-disconnected 👌 Tailscale disconnected")

    # Remove local private key
    if os.path.exists(RSA_PRIVATE_PEM_PATH):
        os.remove(RSA_PRIVATE_PEM_PATH)
        logger.info(f"Private key {RSA_PRIVATE_PEM_PATH} deleted.")
    else:
        logger.warning(f"Private key {RSA_PRIVATE_PEM_PATH} not found — nothing to delete.")

    # Remove local public key
    if os.path.exists(RSA_PUBLIC_PEM_PATH):
        os.remove(RSA_PUBLIC_PEM_PATH)
        logger.info(f"Public key {RSA_PUBLIC_PEM_PATH} deleted.")
    else:
        logger.warning(f"Public key {RSA_PUBLIC_PEM_PATH} not found — nothing to delete.")
    
    return True

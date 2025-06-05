import json
import time

from client.front.config import UDP_SEND_LOG_DELAY, GCS_RC_RECV_PORT
from tech_utils.udp import get_socket
from tech_utils.logger import init_logger

logger = init_logger("Front_BCK_Sender")

# Create UDP socket
sock = get_socket()

# Stores the timestamp of the last log message per session
_last_log_map = {}


def send_rc_frame(session_id, rc_state, source):
    """
    Sends RC (Remote Control) state to the backend over UDP.

    Args:
        session_id (str): Unique identifier for the current session.
        rc_state (dict): The RC control values to send.
        source (str): The controller type or source ID (unused here but could be logged).

    Behavior:
        - Converts the RC state to JSON and sends it over UDP to the backend.
        - Logs the frame send only if sufficient time has passed since the last log.
    """
    global _last_log_map, sock
    now = time.time()
    json_data = json.dumps(rc_state).encode('utf-8')

    try:
        sock.sendto(json_data, ("127.0.0.1", GCS_RC_RECV_PORT))

        last_logged = _last_log_map.get(session_id, 0)
        if now - last_logged >= UDP_SEND_LOG_DELAY:
            logger.info(f"RC frame sent to 127.0.0.1:{GCS_RC_RECV_PORT} JSON: {rc_state}")
            _last_log_map[session_id] = now

    except Exception as e:
        logger.error(f"Error sending RC frame via UDP: {e}", exc_info=True)

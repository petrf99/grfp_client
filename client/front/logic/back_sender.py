import json
import time

from client.front.config import UDP_SEND_LOG_DELAY, GCS_RC_RECV_PORT

from tech_utils.udp import get_socket
sock = get_socket()

from tech_utils.logger import init_logger
logger = init_logger("Front_BCK_Sender")

_last_log_map = {}
def send_rc_frame(sock, session_id, rc_state, source):
    global _last_log_map
    now = time.time()
    json_data = json.dumps(rc_state).encode('utf-8')

    try:
        sock.sendto(json_data, ("127.0.0.1", GCS_RC_RECV_PORT))
        last = _last_log_map.get(session_id, 0)
        if now - last >= UDP_SEND_LOG_DELAY:
            logger.info(f"Frame sent to 127.0.0.1:{GCS_RC_RECV_PORT} JSON:{rc_state}")
            _last_log_map[session_id] = now
    except Exception as e:
        logger.error(f"Exception occurred while sending UDP: {e}", exc_info=True)
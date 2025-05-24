import json
import time
import socket
import ipaddress

from client.config import UDP_SEND_LOG_DELAY, GCS_RC_RECV_PORT, CLIENT_TLMT_RECV_PORT, CLIENT_VID_RECV_PORT

from tech_utils.logger import init_logger
logger = init_logger("ClientUDP")


_last_log_map = {}
def send_rc_frame(sock, session_id, rc_state, source, gcs_ip):
    global _last_log_map
    now = time.time()
    rc_frame = {
            "timestamp": now,
            "session_id": session_id,
            "source": source,
            "channels": rc_state
        }
    json_data = json.dumps(rc_frame).encode('utf-8')

    try:
        try:
            ipaddress.ip_address(gcs_ip)
        except ValueError:
            logger.error(f"Invalid IP: {gcs_ip}")
            return
        sock.sendto(json_data, (gcs_ip, GCS_RC_RECV_PORT))
        last = _last_log_map.get(session_id, 0)
        if now - last >= UDP_SEND_LOG_DELAY:
            logger.info(f"Frame sent to {gcs_ip}:{GCS_RC_RECV_PORT}\nJSON:\n{rc_frame}\n")
            _last_log_map[session_id] = now
    except Exception as e:
        logger.error(f"Exception occurred while sending UDP: {e}\n", exc_info=True)
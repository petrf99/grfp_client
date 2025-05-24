from tech_utils.logger import init_logger
logger = init_logger("Front_Back_Interaction")

def stop(sesssion_id = None, finish_flg = False):
    return 0

def start_session(session_id):
    return 0

def launch_streams(session_id):
    return 0



import json
import time

from client.config import UDP_SEND_LOG_DELAY, LOCAL_RC_PORT

from tech_utils.udp import get_socket
sock = get_socket()

_last_log_map = {}
def send_rc_frame(session_id, rc_state, source):
    global _last_log_map, sock
    now = time.time()
    rc_frame = {
            "timestamp": now,
            "session_id": session_id,
            "source": source,
            "channels": rc_state
        }
    json_data = json.dumps(rc_frame).encode('utf-8')

    try:
        sock.sendto(json_data, ("127.0.0.1", LOCAL_RC_PORT))
        last = _last_log_map.get(session_id, 0)
        if now - last >= UDP_SEND_LOG_DELAY:
            logger.info(f"Frame sent to 127.0.0.1:{LOCAL_RC_PORT}\nJSON:\n{rc_frame}\n")
            _last_log_map[session_id] = now
    except Exception as e:
        logger.error(f"Exception occurred while sending UDP: {e}\n", exc_info=True)
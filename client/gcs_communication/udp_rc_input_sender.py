import json
import time
import socket

from client.config import UDP_SEND_LOG_DELAY, GCS_UDP_PORT, CLIENT_UDP_PORT

from tech_utils.logger import init_logger
logger = init_logger("RCClientUDP")

# === Создание UDP-сокета ===
def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", CLIENT_UDP_PORT))  # чтобы слушать телеметрию
    return sock


last_out_log_time = 0
def send_rc_frame(sock, session_id, rc_state, source, gcs_ip):
    global last_out_log_time
    rc_frame = {
            "timestamp": time.time(),
            "session_id": session_id,
            "source": source,
            "channels": rc_state
        }
    json_data = json.dumps(rc_frame).encode('utf-8')

    try:
        sock.sendto(json_data, (gcs_ip, GCS_UDP_PORT))
        current_time = time.time()
        if current_time - last_out_log_time >= UDP_SEND_LOG_DELAY:
            logger.info(f"Frame sent to {gcs_ip}:{GCS_UDP_PORT}\nJSON:\n{rc_frame}\n")
            last_out_log_time = current_time
    except Exception as e:
        logger.error(f"Exception occurred while sending UDP: {e}\n", exc_info=True)
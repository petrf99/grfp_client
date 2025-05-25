import cv2
import json
import time

from tech_utils.logger import init_logger
logger = init_logger("Front_UDP_Listeners")

from client.front.config import CLIENT_VID_RECV_PORT

# 🎥 Подключение к локальному видео-порту
def get_video_cap(n_attempts):
    for _ in range(n_attempts):
        cap = cv2.VideoCapture(f"udp://@:{CLIENT_VID_RECV_PORT}?fifo_size=5000000&overrun_nonfatal=1")
        if cap.isOpened():
            return cap
        time.sleep(0.1)
    else:
        logger.error("Failed to open video stream after retries")
        return False
    
import socket
from client.front.logic.back_listener import sess_state

telemetry_data = {}

def get_telemetry(tlmt_sock):
    global telemetry_data
    try:
        while not sess_state.abort_event.is_set() and not sess_state.finish_event.is_set():
            data, addr = tlmt_sock.recvfrom(65536)
            telemetry_data = json.loads(data)
            cur_time = time.time()
            init_timestamp = telemetry_data.get("rc_channels", {}).get("init_timestamp")
            if init_timestamp:
                telemetry_data["round_trip_time_ms"] = int(1000*(cur_time - init_timestamp))
    except socket.timeout:
        pass
    except OSError as e:
        logger.warning(f"Telemetry receiver socker closed {e}")
        return {}
    except Exception as e:
        logger.error(f"Telemetry receiver error: {e}")
        return {}
    
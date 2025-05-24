import cv2
import json
import time

from tech_utils.logger import init_logger
logger = init_logger("Front_GUI")

from client.config import LOCAL_VIDEO_PORT, LOCAL_TLMT_PORT

# 🎥 Подключение к локальному видео-порту
def get_video_cap(n_attempts):
    for _ in range(n_attempts):
        cap = cv2.VideoCapture(f"udp://@:{LOCAL_VIDEO_PORT}?fifo_size=5000000&overrun_nonfatal=1")
        if cap.isOpened():
            return cap
        time.sleep(0.1)
    else:
        logger.error("Failed to open video stream after retries")
        return False
    
from tech_utils.udp import get_socket
tlmt_sock = get_socket("127.0.0.1", LOCAL_TLMT_PORT, bind=True)

def get_telemetry():
    global tmlt_sock
    try:
        data, addr = tmlt_sock.recvfrom(65536)
        telemetry_data = json.loads(data)
        cur_time = time.time()
        telemetry_data["round_trip_time_ms"] = int(1000*(cur_time - telemetry_data.get("rc_channels", {}.get("init_timestamp"))))
        return telemetry_data
    except tmlt_sock.timeout:
        return False
    except OSError as e:
        logger.warning(f"Telemetry receiver socker closed {e}")
        return False
    except Exception as e:
        logger.error(f"Telemetry receiver error: {e}")
        return False
    
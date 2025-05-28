import subprocess
import json
import time
import socket

from tech_utils.logger import init_logger
logger = init_logger("Front_UDP_Listeners")

from client.front.config import CLIENT_VID_RECV_PORT

def get_video_resolution():
    cmd = [
        "ffprobe",
        "-v", "error",  # выводим только ошибки
        "-select_streams", "v:0",  # выбираем первый видеопоток
        "-show_entries", "stream=width,height",  # запрашиваем ширину и высоту
        "-of", "json",  # формат вывода — JSON
        f"udp://@:{CLIENT_VID_RECV_PORT}"  # источник — UDP поток на указанном порту
    ]

    out = subprocess.run(cmd, capture_output=True)
    info = json.loads(out.stdout)
    w = info['streams'][0]['width']
    h = info['streams'][0]['height']
    return w, h


# 🎥 Подключение к локальному видео-порту
def get_video_cap(n_attempts):
    ffmpeg_recv_cmd = [
        "ffmpeg",
        "-fflags", "+discardcorrupt",
        "-flags", "low_delay",
        "-probesize", "500000",
        "-analyzeduration", "1000000",
        "-i", f"udp://@:{CLIENT_VID_RECV_PORT}?fifo_size=1000000&overrun_nonfatal=1",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-"
    ]


    return subprocess.Popen(ffmpeg_recv_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

telemetry_data = {}

def get_telemetry(tlmt_sock):
    from client.front.state import front_state
    global telemetry_data
    try:
        while not front_state.finish_event.is_set() and not front_state.abort_event.is_set():
            try:
                data, addr = tlmt_sock.recvfrom(65536)
                telemetry_data.clear()
                telemetry_data.update(json.loads(data))
                cur_time = time.time()
                init_timestamp = telemetry_data.get("rc_channels", {}).get("init_timestamp")
                if init_timestamp:
                    telemetry_data["round_trip_time_ms"] = int(1000*(cur_time - init_timestamp))
            except socket.timeout:
                pass
    except OSError as e:
        logger.warning(f"Telemetry receiver socker closed {e}")
    except Exception as e:
        logger.error(f"Telemetry receiver error: {e}")
    
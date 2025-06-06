import subprocess
import threading
import json
import time
import socket
from tech_utils.safe_subp_run import safe_subp_run

from client.front.config import CLIENT_VID_RECV_PORT, CLIENT_TLMT_RECV_PORT

from tech_utils.logger import init_logger
logger = init_logger("Front_UDP_Listeners")

class FrameBuffer:
    def __init__(self):
        self.lock = threading.Lock()
        self.frame = None

    def put(self, frame):
        with self.lock:
            self.frame = frame  # просто перезаписываем

    def get(self):
        with self.lock:
            return self.frame

def ffmpeg_reader(cap, frame_size, frame_buffer, running_event):
    while running_event.is_set():
        try:
            raw_frame = cap.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                continue
            frame_buffer.put(raw_frame)  # заменяет предыдущий кадр
        except Exception as e:
            logger.warning(f"FFMPEG Reader error: {e}")
            continue


# 📏 Get the video resolution (width x height) from the incoming UDP stream using ffprobe
def get_video_resolution():
    cmd = [
        "ffprobe",
        "-v", "error",  # show only errors
        "-select_streams", "v:0",  # select the first video stream
        "-show_entries", "stream=width,height",  # request width and height info
        "-of", "json",  # output format as JSON
        f"udp://@:{CLIENT_VID_RECV_PORT}?timeout=5000000"  # video source: UDP stream on specified port
    ]

    n_attempts = 1000
    k = 0
    info = None
    while (not info or not isinstance(info, dict) or "streams" not in info) and k <= n_attempts:
        out = safe_subp_run(cmd, retries=100, timeout=10, check=True, capture_output=True)
        info = json.loads(out.stdout)
        if not info or not isinstance(info, dict) or "streams" not in info:
            logger.error("Can't get video resolution.")
            k += 1
            continue
        w = info['streams'][0]['width']
        h = info['streams'][0]['height']
        logger.info(f"Video resolution {w}x{h} obtained")
        return w, h


# 🎥 Connect to the local UDP video port and start receiving raw video frames via ffmpeg
def get_video_cap():
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
    logger.info(f"Start listen video on port {CLIENT_VID_RECV_PORT}")

    return subprocess.Popen(ffmpeg_recv_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)


# 📡 Global telemetry data storage
telemetry_data = {}

from tech_utils.udp import get_socket

# 📡 Start listening for telemetry data on the given socket and update telemetry state
def get_telemetry():
    # Set up sockets for sending RC and receiving telemetry
    tlmt_sock = get_socket("0.0.0.0", CLIENT_TLMT_RECV_PORT, bind=True)
    from client.front.state import front_state
    global telemetry_data
    try:
        while front_state.running_event.is_set():
            try:
                data, addr = tlmt_sock.recvfrom(65536)
                telemetry_data.clear()
                telemetry_data.update(json.loads(data))
                
                # Calculate round-trip time (RTT) for RC channel timestamps if available
                cur_time = time.time()
                init_timestamp = telemetry_data.get("rc_channels", {}).get("init_timestamp")
                if init_timestamp:
                    telemetry_data["round_trip_time_ms"] = int(1000 * (cur_time - init_timestamp))
            except socket.timeout:
                pass  # Normal case if no data received yet
    except OSError as e:
        logger.warning(f"Telemetry receiver socket closed: {e}")
    except Exception as e:
        logger.error(f"Telemetry receiver error: {e}")
    finally:
        tlmt_sock.close()

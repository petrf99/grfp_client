import subprocess
import json
import time
import socket

from tech_utils.logger import init_logger
logger = init_logger("Front_UDP_Listeners")

from client.front.config import CLIENT_VID_RECV_PORT

# 📏 Get the video resolution (width x height) from the incoming UDP stream using ffprobe
def get_video_resolution():
    cmd = [
        "ffprobe",
        "-v", "error",  # show only errors
        "-select_streams", "v:0",  # select the first video stream
        "-show_entries", "stream=width,height",  # request width and height info
        "-of", "json",  # output format as JSON
        f"udp://@:{CLIENT_VID_RECV_PORT}"  # video source: UDP stream on specified port
    ]

    out = subprocess.run(cmd, capture_output=True)
    info = json.loads(out.stdout)
    w = info['streams'][0]['width']
    h = info['streams'][0]['height']
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

    return subprocess.Popen(ffmpeg_recv_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)


# 📡 Global telemetry data storage
telemetry_data = {}

# 📡 Start listening for telemetry data on the given socket and update telemetry state
def get_telemetry(tlmt_sock):
    from client.front.state import front_state
    global telemetry_data
    try:
        while not front_state.finish_event.is_set() and not front_state.abort_event.is_set():
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

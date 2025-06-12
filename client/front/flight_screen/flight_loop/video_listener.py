# Get video from UDP-port via ffmpeg
import numpy as np
import time
import threading
import subprocess
import json
import cv2

from client.front.config import (
    NO_FRAME_MAX, CLIENT_VID_RECV_PORT
)
from tech_utils.udp_listener import RingBuffer
from tech_utils.safe_subp_run import safe_subp_run
from tech_utils.ffmpeg_accel import run_ffmpeg_decoder_with_hwaccel

from tech_utils.logger import init_logger
logger = init_logger("Front_VID_Listener")

def ffmpeg_reader(cap, frame_size, frame_buffer: RingBuffer, running_event):
    while running_event.is_set():
        try:
            raw_frame = cap.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                continue
            frame_buffer.set(val=raw_frame, addr=None)  # заменяет предыдущий кадр
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
        "-pix_fmt", "yuv420p",
        "-"
    ]
    logger.info(f"Start listen video on port {CLIENT_VID_RECV_PORT}")

    return run_ffmpeg_decoder_with_hwaccel(ffmpeg_recv_cmd)


# Main function
def get_video():
    from client.front.state import front_state
    session_id = front_state.session_id

    cap = None

    # Determine video resolution and frame size
    width, height = get_video_resolution()
    frame_size = width * height * 3 // 2

    # Resize GUI window according to video resolution
    front_state.flight_screen.set_video_size((width, height))

    try:
        frame_buffer = RingBuffer()
        cap = get_video_cap()

        reader_thread = threading.Thread(
            target=ffmpeg_reader,
            args=(cap, frame_size, frame_buffer, front_state.running_event),
            daemon=True
        )
        reader_thread.start()

        no_frame_counter = 0
        logger.info("Flight loop starting")

        while front_state.running_event.is_set():

            # 🎥 Read video frame
            raw_frame = frame_buffer.get()
            if raw_frame is None or len(raw_frame) != frame_size:
                time.sleep(0.001)
                continue

            # Собираем сырое YUV420P в плоский массив
            mv = memoryview(raw_frame)
            yuv = np.frombuffer(mv, dtype=np.uint8).reshape((height * 3 // 2, width))

            # Конвертируем одной командой
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB_I420)

            if frame is not None and frame.size != 0:
                no_frame_counter = 0
                front_state.flight_screen.set_video_frame(frame)
            else:
                no_frame_counter += 1
                if no_frame_counter >= NO_FRAME_MAX:
                    logger.warning("🔁 Reinitializing video stream...")
                    if cap and hasattr(cap, "kill"):
                        cap.kill()
                    cap = get_video_cap()
                    reader_thread.join(timeout=2)
                    reader_thread = threading.Thread(
                        target=ffmpeg_reader,
                        args=(cap, frame_size, frame_buffer, front_state.running_event),
                        daemon=True
                    )
                    reader_thread.start()
                    no_frame_counter = 0
                else:
                    logger.warning("⚠️ Frame not received — waiting...")
                    time.sleep(0.1)
                continue

        logger.info("Flight loop exited due to event set")

    except KeyboardInterrupt:
        logger.warning("User interrupted during loop(). Aborting session.")
        front_state.running_event.clear()
        #return False

    except Exception as e:
        logger.error(f"{session_id} Flight Loop Error: {e}")
        front_state.running_event.clear()
        #return False

    finally:
        logger.info("Closing Flight loop")

        # Graceful shutdown
        reader_thread.join(timeout=2)
        if cap:
            cap.terminate()
            try:
                cap.wait(timeout=2)
            except subprocess.TimeoutExpired:
                cap.kill()
        else:
            logger.warning("No cap found to close")

        logger.info("Flight loop terminated")
        return front_state.running_event.is_set()

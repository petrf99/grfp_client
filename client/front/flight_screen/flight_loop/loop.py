import numpy as np
import time
import threading
import subprocess

from tech_utils.logger import init_logger
logger = init_logger("Front_FlightLoop")

from client.front.config import (
    NO_FRAME_MAX, CLIENT_TLMT_RECV_PORT
)

from client.front.logic.data_listeners import (
    get_video_resolution, get_video_cap, get_telemetry, telemetry_data
)

from tech_utils.udp import get_socket


def loop():
    from client.front.state import front_state
    session_id = front_state.session_id

    # Set up sockets for sending RC and receiving telemetry
    tlmt_sock = get_socket("0.0.0.0", CLIENT_TLMT_RECV_PORT, bind=True)

    cap = None

    # Determine video resolution and frame size
    width, height = get_video_resolution()
    frame_size = width * height * 3

    # Resize GUI window according to video resolution
    front_state.flight_screen.set_video_size([height, width])

    time.sleep(0.2)  # Brief pause before start-up

    try:
        cap = get_video_cap()

        threading.Thread(target=get_telemetry, args=(tlmt_sock,), daemon=True).start()

        no_frame_counter = 0
        logger.info("Flight loop starting")

        while not front_state.finish_event.is_set() and not front_state.abort_event.is_set():

            # 🎥 Read video frame
            raw_frame = cap.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                # logger.warning("⚠️ Invalid frame size. Recalculating")
                continue

            frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
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
                    no_frame_counter = 0
                else:
                    logger.warning("⚠️ Frame not received — waiting...")
                    time.sleep(0.1)
                continue


    except KeyboardInterrupt:
        logger.warning("User interrupted during loop(). Aborting session.")
        front_state.abort_event.set()
        return False

    except Exception as e:
        logger.error(f"{session_id} Flight Loop Error: {e}")
        front_state.abort_event.set()
        return False

    finally:
        # Graceful shutdown
        if tlmt_sock:
            tlmt_sock.close()

        if cap:
            cap.terminate()
            try:
                cap.wait(timeout=2)
            except subprocess.TimeoutExpired:
                cap.kill()

    return front_state.finish_event.is_set()

import numpy as np
import pygame
import time
import threading
import subprocess

from tech_utils.logger import init_logger
logger = init_logger("Front_GUI")

from client.front.config import (
    SCREEN_HEIGHT, SCREEN_WIDTH, FREQUENCY, RC_CHANNELS_DEFAULTS,
    TELEMETRY_GUI_DRAW_FIELDS, NO_FRAME_MAX, CLIENT_TLMT_RECV_PORT,
    CONTROLLER_PATH, CONTROLLERS_LIST, BACKEND_CONTROLLER
)

from client.front.logic.data_listeners import (
    get_video_resolution, get_video_cap, get_telemetry, telemetry_data
)

from client.front.flight_screen.gui.pygame import (
    pygame_init, pygame_event_get, pygame_quit, pygame_QUIT
)

from client.front.logic.back_sender import send_rc_frame
from client.front.inputs import get_rc_input

from tech_utils.udp import get_socket


def gui_loop():
    from client.front.state import front_state
    session_id = front_state.session_id

    # Load selected controller
    with open(CONTROLLER_PATH, "r") as f:
        text = f.read().strip()
        controller = text if text in CONTROLLERS_LIST else None

    # rc_input = None if controller in BACKEND_CONTROLLER else get_rc_input(controller)

    # Determine video resolution and frame size
    width, height = get_video_resolution()
    frame_size = width * height * 3

    # Resize GUI window according to video resolution
    front_state.flight_screen.set_video_size([height, width])

    time.sleep(0.2)  # Brief pause before setup

    try:
        telemetry_values = {'no data': ''}

        cap = get_video_cap()

        # Set up sockets for sending RC and receiving telemetry
        sock = get_socket()
        tlmt_sock = get_socket("0.0.0.0", CLIENT_TLMT_RECV_PORT, bind=True)

        threading.Thread(target=get_telemetry, args=(tlmt_sock,), daemon=True).start()

        no_frame_counter = 0
        logger.info("GUI loop starting")

        while not front_state.finish_event.is_set() and not front_state.abort_event.is_set():
            # 📤 Send RC state to backend
            # send_rc_frame(sock, session_id, rc_state, controller)

            # 🎥 Read video frame
            raw_frame = cap.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                # logger.warning("⚠️ Invalid frame size. Recalculating")
                continue

            frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
            if frame is not None and frame.size != 0:
                no_frame_counter = 0
                #frame = np.flip(frame, axis=0)
                #frame = np.fliplr(frame) 
                # frame = np.rot90(frame, k=-1)
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

            # 📡 Draw telemetry HUD
            hud_lines = []
            telemetry_snapshot = telemetry_data.copy()
            telemetry_values = telemetry_snapshot if isinstance(telemetry_snapshot, dict) else {'no data': ''}
            front_state.flight_screen.set_telemetry_data(telemetry_values)

    except KeyboardInterrupt:
        logger.warning("User interrupted during gui_loop(). Aborting session.")
        front_state.abort_event.set()
        return False

    except Exception as e:
        logger.error(f"{session_id} GUI Loop Error: {e}")
        front_state.abort_event.set()
        return False

    finally:
        # Graceful shutdown
        sock.close()
        tlmt_sock.close()

        cap.terminate()
        try:
            cap.wait(timeout=2)
        except subprocess.TimeoutExpired:
            cap.kill()

        #pygame_quit()

    return front_state.finish_event.is_set()

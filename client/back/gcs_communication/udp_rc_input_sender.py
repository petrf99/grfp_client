import orjson
import time
import socket

from tech_utils.logger import init_logger
logger = init_logger("Back_RC_Streamer")

from client.back.config import BACKEND_CONTROLLER, BACK_UDP_PORT, RC_CHANNELS_DEFAULTS, UDP_SEND_LOG_DELAY
from tech_utils.udp_listener import UDPListener
from tech_utils.udp import get_socket
from client.back.state import client_state
from client.back.front_communication.front_msg_sender import send_message_to_front

# Streams RC input data to GCS via UDP
def stream_rc_to_gcs():
    send_message_to_front("📡 Starting RC-input streamer...")
    logger.info("Starting RC-input streamer")

    front_rc_flg = False  # Flag for choosing RC input source (Front vs Back)
    listener = None

    # If RC source is the frontend, bind to a port and listen
    if client_state.controller not in BACKEND_CONTROLLER:
        logger.info("Assigned to restream RC from Front")
        front_rc_flg = True
        listener = UDPListener(BACK_UDP_PORT)
        sock = listener.get_sock()
    else:
        # If controller is local (backend), prepare to send RC data
        sock = get_socket(host=None, port=None, bind=False)
        logger.info("Assigned to stream RC from Back")
    
    last_inp_log_time = 0  # Timestamp of last log to avoid spamming

    try:
        # Main loop: runs while session is running
        while client_state.running_event.is_set():
            cur_time = time.time()

            try:
                rc_frame = {
                    "timestamp": cur_time,
                    "session_id": client_state.session_id,
                    "source": client_state.controller,
                }

                # Get RC data: from Front (via UDP) or use default mock values
                if front_rc_flg:
                    data = listener.get_latest()
                    if not data:
                        time.sleep(0.001)
                        continue
                    else:
                        rc_frame["channels"] = data
                else:
                    rc_frame["channels"] = RC_CHANNELS_DEFAULTS.copy()  # TODO: Replace with actual controller input
                
                # Send RC frame to GCS
                json_data = orjson.dumps(rc_frame)
                sock.sendto(json_data, (client_state.gcs_ip, client_state.gcs_rc_port))

                # Log sent RC frame periodically
                if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                    logger.info(f"RC-input {json_data} sent to GCS on {client_state.gcs_ip}:{client_state.gcs_rc_port}")
                    last_inp_log_time = cur_time

            except socket.timeout:
                continue  # Just retry on timeout
            except OSError as e:
                send_message_to_front("🛑 RC-input streamer socket closed.")
                logger.warning(f"RC-input streamer socket closed {e}")
                break
            except Exception as e:
                send_message_to_front(f"⚠️ RC-input streamer error: {e}")
                logger.error(f"RC-input streamer error: {e}")

    except KeyboardInterrupt:
        send_message_to_front("🛑 RC-input streamer interrupted by user.")
        logger.warning("RC-input streamer interrupted by user.")
    finally:
        if listener:
            listener.stop()
        if sock:
            sock.close()

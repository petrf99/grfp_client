import json
import time
import socket

from tech_utils.logger import init_logger
logger = init_logger("Back_RC_Streamer")


from client.back.config import BACKEND_CONTROLLER, GCS_RC_RECV_PORT, RC_CHANNELS_DEFAULTS, UDP_SEND_LOG_DELAY
from tech_utils.udp import get_socket
from client.back.session_manager.state import sess_state
from client.back.front_communication.front_msg_sender import send_message_to_front

def stream_rc_to_gcs(session_id, controller, gcs_ip):

    send_message_to_front("📡 Starting RC-input streamer...")
    logger.info("Starting RC-input streamer")
    front_rc_flg = False
    sock = None
    if controller not in BACKEND_CONTROLLER:
        logger.info("Assigned to restream RC from Front")
        front_rc_flg = True
        sock = get_socket("0.0.0.0", GCS_RC_RECV_PORT, bind=True)
    else:
        sock = get_socket(host=None, port=None, bind=False)
        logger.info("Assigned to stream RC from Back")
    
    last_inp_log_time = 0
    try:
        while not sess_state.finish_event.is_set() and not sess_state.abort_event.is_set():
            cur_time = time.time()
            try:
                rc_frame = {
                            "timestamp": cur_time,
                            "session_id": session_id,
                            "source": controller,
                        }
                if front_rc_flg:
                    data, addr = sock.recvfrom(65536)
                    rc_frame["channels"] = json.loads(data)
                else:
                    rc_frame["channels"] = json.loads(RC_CHANNELS_DEFAULTS) # Mock value
                        
                
                json_data = json.dumps(rc_frame).encode('utf-8')
                sock.sendto(json_data, (gcs_ip, GCS_RC_RECV_PORT))

                if cur_time - last_inp_log_time >= UDP_SEND_LOG_DELAY:
                    logger.info(f"RC-input {json_data} sent to GCS on {gcs_ip}:{GCS_RC_RECV_PORT}")
                    last_inp_log_time = cur_time
            except socket.timeout:
                continue
            except OSError as e:
                send_message_to_front("🛑 RC-input streamer socket closed.")
                logger.warning(f"RC-input streamer socket closed {e}")
                break
            except Exception as e:
                send_message_to_front(f"⚠️ RC-input streamer error: {e}")
                logger.error(f"RC-input streamer RC streamer error: {e}")
    except KeyboardInterrupt:
        send_message_to_front("🛑 RC-input streamer interrupted by user.")
        logger.warning("RC-input streamer interrupted by user.")
    finally:
        sock.close()

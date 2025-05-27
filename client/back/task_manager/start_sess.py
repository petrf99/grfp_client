from client.back.front_communication.front_msg_sender import send_message_to_front
from client.back.state import client_state
from client.back.gcs_communication.tcp_communication import send_start_message_to_gcs
from client.back.gcs_communication.tcp_communication import keep_connection
from client.back.gcs_communication.udp_rc_input_sender import stream_rc_to_gcs

import threading

from tech_utils.logger import init_logger
logger = init_logger("Back_SessStarter")

def start_session():
    if not send_start_message_to_gcs():
        logger.error(f"Start session failed on handshake with GCS {client_state}")
        return False
    
    threading.Thread(target=keep_connection, daemon=True).start()

    threading.Thread(target=stream_rc_to_gcs, daemon=True).start()

    send_message_to_front("✅ Session started")
    logger.info(f"Session started {client_state}")
    return True


    
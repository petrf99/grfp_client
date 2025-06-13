from client.back.front_communication.front_msg_sender import send_message_to_front
from client.back.state import client_state
from client.back.gcs_communication.tcp_communication import send_start_message_to_gcs
from client.back.gcs_communication.tcp_communication import keep_connection
from client.back.gcs_communication.udp_rc_input_sender import stream_rc_to_gcs

import threading

from tech_utils.logger import init_logger
logger = init_logger(name="SessStarter", component="back")

# Starts a remote session with the GCS
def start_session():
    # 0. Set client_state.running_event
    client_state.running_event.set()

    # 1. Perform TCP handshake with GCS to establish session
    if not send_start_message_to_gcs():
        send_message_to_front("abort")
        logger.error(f"Start session failed on handshake with GCS {client_state}")
        return False
    
    # 2. Start background thread to periodically ping GCS to ensure connection stays alive
    threading.Thread(target=keep_connection, daemon=True).start()

    # 3. Start background thread to send RC (remote control) data to GCS via UDP
    threading.Thread(target=stream_rc_to_gcs, daemon=True).start()

    # 4. Notify front-end and log session start
    send_message_to_front("✅ Session started")
    logger.info(f"Session started {client_state}")
    return True

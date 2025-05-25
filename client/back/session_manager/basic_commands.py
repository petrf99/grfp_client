import requests

from tech_utils.logger import init_logger
logger = init_logger("Back_BasicCmds")

from client.back.config import GCS_TCP_PORT

from client.back.session_manager.state import sess_state
from client.back.front_communication.front_msg_sender import send_message_to_front

SESSION_ABORTED='abort'
SESSION_FINISHED='finish'
def close(gcs_ip, session_id, finish_flg = False):
    send_message_to_front("Closing session...")
    status = SESSION_ABORTED
    if finish_flg:
        status = SESSION_FINISHED
        
    if not sess_state.external_stop_event.is_set():
        url = f"http://{gcs_ip}:{GCS_TCP_PORT}/send-message"
        payload = {
            "session_id": session_id,
            "message": f"{status}-session"
        }
        send_message_to_front(f"📡 Sending {status}-session to GCS at {gcs_ip}...")
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                send_message_to_front(f"Message {status}-session successfully sent to GCS.")
                logger.info(f"{session_id} {status} message sent to GCS")
        except Exception as e:
            send_message_to_front(f"Something went wront. Terminating session forcedly...")
            logger.error(f"{session_id} Can't send {status} message to GCS. Exception: {e}. Terminating forcedly.")
    
    return disconnect()

from tech_utils.tailscale import tailscale_down
def disconnect():
    tailscale_down()

    #from client.back.gcs_communication.tcp_communication import shutdown_client_server
    #if not shutdown_client_server():
    #    send_ws_message("Could not finish TCP server correctly.")
    #    return False
    sess_state.clear()
    return True

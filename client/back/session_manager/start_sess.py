from client.back.session_manager.basic_commands import disconnect
from client.back.front_communication.front_msg_sender import send_message_to_front
from client.back.session_manager.state import sess_state
from client.back.gcs_communication.tailscale_connect import start_tailscale, wait_for_tailscale_ips
from client.back.gcs_communication.tcp_communication import send_start_message_to_gcs, run_client_server
from client.back.gcs_communication.tcp_communication import keep_connection

from tech_utils.logger import init_logger
logger = init_logger("Back_SessStarter")

def connect_job(session_id, auth_token, tag):
    if not start_tailscale(session_id, auth_token, tag):
        return False
    
    send_message_to_front("Tailscale started")
    
    ips = wait_for_tailscale_ips(session_id, auth_token)
    if not ips:
        send_message_to_front("abort")
        return disconnect()
    
    send_message_to_front("Tailscale IP of GCS retrieved")
    
    run_client_server()

    send_message_to_front("TCP server is run")
    
    sess_state.gcs_ip = ips[0]

    if not send_start_message_to_gcs(sess_state.gcs_ip, sess_state.session_id):
        send_message_to_front('abort')
        return disconnect()
    
    threading.Thread(target=keep_connection, args = (sess_state.gcs_ip, session_id), daemon=True).start()
    
    send_message_to_front("All set")
    send_message_to_front("connected")
    return True
    
import threading
def connect(session_id, auth_token, tag):
    try:
        threading.Thread(target=connect_job, args=(session_id, auth_token, tag), daemon=True).start()
        return True
    except:
        return False


from client.back.gcs_communication.udp_rc_input_sender import stream_rc_to_gcs
def launch_sess(session_id):
    try:
        threading.Thread(target=stream_rc_to_gcs, args=(sess_state.session_id, sess_state.controller, sess_state.gcs_ip), daemon=True).start()
        return True
    except:
        return False
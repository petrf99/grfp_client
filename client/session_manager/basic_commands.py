import requests
import subprocess

from tech_utils.logger import init_logger
logger = init_logger("Client_Main")

from client.config import CLIENT_TCP_PORT, GCS_TCP_PORT

from client.session_manager.events import external_stop_event

SESSION_ABORTED='abort'
SESSION_FINISHED='finish'
def close(gcs_ip, session_id, sock = None, finish_flg = False):
    print("Closing session...")
    status = SESSION_ABORTED
    if finish_flg:
        status = SESSION_FINISHED
    if sock:
        try:
            sock.close()
        except Exception:
            pass
        
    if not external_stop_event.is_set():
        url = f"http://{gcs_ip}:{GCS_TCP_PORT}/send-message"
        payload = {
            "session_id": session_id,
            "message": f"{status}-session"
        }
        print(f"📡 Sending {status}-session to GCS at {gcs_ip}...")
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                print(f"Message {status}-session successfully sent to GCS.")
                logger.info(f"{session_id} {status} message sent to GCS")
        except Exception as e:
            print(f"Something went wront. Terminating session forcedly...")
            logger.error(f"{session_id} Can't send {status} message to GCS. Exception: {e}. Terminating forcedly.")
    
    return disconnect()

from tech_utils.tailscale import tailscale_down
def disconnect():
    tailscale_down()

    from client.gcs_communication.tcp_communication import shutdown_client_server
    if not shutdown_client_server():
        print("Could not finish TCP server correctly.")

    return leave()

def leave():
    print("See you next flight!")
    logger.info("Exit the program")
    return True
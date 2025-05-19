import requests
import subprocess

from tech_utils.logger import init_logger
logger = init_logger("RCClient_SessManager")

from client.config import CLIENT_TCP_PORT, GCS_TCP_PORT

from client.gcs_communication.tcp_communication import shutdown_client_server

def ready():
    print("If you are ready to fly, please type 'ready'.\nOr type 'abort' to terminate the process.")
    while True:
        cmd = input().strip().lower()
        if cmd == 'ready':
            return True
        elif cmd == 'abort':
            return False
        else:
            print("Please type 'ready' or 'abort'")

def disconnect(gcs_ip, session_id, sock = None, good = False):
    status = 'abort'
    if good:
        status = 'finish'
    if sock:
        try:
            sock.close()
        except Exception:
            pass
    url = f"http://{gcs_ip}:{GCS_TCP_PORT}/send-message"
    payload = {
        "session_id": session_id,
        "message": f"{status}_session"
    }
    print(f"📡 Sending {status}_session to GCS at {gcs_ip}...")
    try:
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            print(f"{status} successfully sent.")
            logger.info(f"{session_id} {status} message sent to GCS")
    except Exception as e:
        print(f"Something went wront. Terminating session forcedly...")
        logger.error(f"{session_id} Can't send {status} message to GCS. Exception: {e}. Terminating forcedly.")
    
    return close()
    
def close():
    try:
        print("🔌 Stopping Tailscale VPN...")
        subprocess.run(["sudo", "tailscale", "down"], check=True)
        print("✅ Tailscale VPN stopped.")
        logger.info("Tailscale VPN stopped")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to stop Tailscale:", e)
        logger.info(f"Failed to stop Tailscale: {e}")

    shutdown_client_server()

    return leave()

def leave():
    print("See you next flight!")
    logger.info("Exit the program")
    return True
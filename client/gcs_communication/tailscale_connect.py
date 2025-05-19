import subprocess

from tech_utils.logger import init_logger
logger = init_logger("RCClient_GCS_Connect")

def start_tailscale(session_id, auth_token: str):
    print("🔧 Starting Tailscale with your mission auth token...")
    hostname = f"client_{session_id}"
    try:
        subprocess.run([
            "sudo", "tailscale", "up", f"--authkey={auth_token}",
            f"--hostname={hostname}"
        ], check=True)
        print("✅ Tailscale started.")
        logger.info(f"{session_id} Tailscale start succeded")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to start Tailscale:", e)
        logger.error(f"{session_id} Tailscale start failed", exc_info=True)
        return False



import time
import requests
from client.config import RFD_IP, RFD_SM_PORT, TAILSCALE_IP_POLL_INTERVAL, TAILSCAPE_IP_TIMEOUT

def wait_for_tailscale_ips(session_id: str) -> tuple[str, str]:
    start = time.time()
    print("🔄 Waiting for GCS and Client to connect on Tailscale...")
    while True:
        try:
            response = requests.get(f"{RFD_IP}:{RFD_SM_PORT}/get-tailscale-ips", params={"session_id": session_id}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                gcs_ip = data.get("gcs_ip")
                client_ip = data.get("client_ip")
                if gcs_ip and client_ip:
                    print(f"✅ Both sides connected. GCS IP: {gcs_ip}, Client IP: {client_ip}")
                    return gcs_ip, client_ip
            else:
                logger.info(f"{session_id} Waiting for tailscale peers to be ready...")
        except Exception as e:
            logger.warning(f"{session_id} Could not query tailscale-ips: {e}")

        time.sleep(TAILSCALE_IP_POLL_INTERVAL)

        if time.time() - start >= TAILSCAPE_IP_TIMEOUT:
            logger.error(f"{session_id} Timeout while waiting for Tailscale IPs")
            return False

from tech_utils.logger import init_logger
logger = init_logger("Client_Tailscale_Connect")


import time
import requests
from typing import Optional

from client.config import RFD_IP, RFD_SM_PORT, TAILSCALE_IP_POLL_INTERVAL, TAILSCAPE_IP_TIMEOUT
from tech_utils.tailscale import tailscale_up

import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()

def start_tailscale(session_id, auth_token, tag):
    hostname = f"{tag}-{session_id[:8]}"
    return tailscale_up(hostname, auth_token)

def wait_for_tailscale_ips(session_id: str, auth_token: str) -> Optional[tuple[str, str]]:
    start = time.time()
    print("🔄 Waiting for GCS to connect on Genesis Private Network...")
    hash_auth_token = hash_token(auth_token)
    try:
        while True:
            try:
                response = requests.post(f"http://{RFD_IP}:{RFD_SM_PORT}/get-tailscale-ips", json={"session_id": session_id, 'hash_auth_token': hash_auth_token}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    gcs_ip = data.get("gcs_ip")
                    client_ip = data.get("client_ip")
                    if gcs_ip and client_ip:
                        print(f"✅ Both sides connected. GCS IP: {gcs_ip}, Client IP: {client_ip}")
                        logger.info(f"{session_id} Connected. GCS: {gcs_ip}, Client: {client_ip}")
                        return gcs_ip, client_ip
                else:
                    logger.info(f"{session_id} Waiting for GCS to be ready...")
                    print("Waiting for GCS to be ready...")
            except Exception as e:
                print("Process failed: Could not connect on Genesis Private Network")
                logger.warning(f"{session_id} Could not query tailscale-ips: {e}")


            time.sleep(TAILSCALE_IP_POLL_INTERVAL)

            if time.time() - start >= TAILSCAPE_IP_TIMEOUT:
                logger.error(f"{session_id} Timeout while waiting for Tailscale IPs")
                print("Process failed: Timeout while connecting to Genesis Private Network")
                return None
            
    except KeyboardInterrupt:
        logger.warning(f"{session_id} Interrupted by user while waiting for Tailscale")
        return None
    

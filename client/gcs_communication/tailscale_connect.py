import subprocess

from tech_utils.logger import init_logger
logger = init_logger("Client_Tailscale_Connect")

import sys
import shutil
import re

from client.config import TS_PATH
    
def get_tailscale_path():
    import os, shutil

    # 1. Из .env
    ts_path = TS_PATH
    if ts_path and os.path.exists(ts_path):
        return ts_path

    # 2. Попробуем which (для Linux/Windows и CLI-установки на macOS)
    found = shutil.which("tailscale")
    if found:
        return found

    # 3. Попробуем путь для GUI-версии на macOS
    gui_path = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
    if os.path.exists(gui_path):
        return gui_path

    raise RuntimeError("❌ Tailscale binary not found. Please install Tailscale or set TS_PATH.")


def needs_sudo_retry(stderr: str, os_name: str) -> bool:
    if not os_name.startswith(("linux", "darwin")):
        return False
    stderr = stderr.lower()
    return any(
        msg in stderr for msg in [
            "failed to connect to local tailscaled",
            "can't connect",
            "permission denied",
            "access denied",
            "connect: permission denied"
        ]
    )

def is_tailscale_installed():
    return shutil.which("tailscale") is not None

def is_tailscale_running_mac():
    try:
        result = subprocess.run([get_tailscale_path(), "status"], capture_output=True, text=True)
        # ищем IP, начинающийся с 100.
        match = re.search(r"\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", result.stdout)
        return result.returncode == 0 and "Logged out." not in result.stdout and bool(match)
    except Exception as e:
        logger.warning(f"Error checking Tailscale status on macOS: {e}")
        return False


def start_tailscale(session_id: str, auth_token: str, tag):
    print("🔧 Starting Tailscale...")

    if not is_tailscale_installed():
        print("❌ Tailscale is not installed on this system.")
        logger.error(f"{session_id} Tailscale start failed — not installed")
        return False

    os_name = sys.platform
    ts_path = get_tailscale_path()
    hostname = f"{tag}-{session_id[:8]}"
    cmd = [ts_path, "up", f"--authkey={auth_token}", f"--hostname={hostname}"]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, shell=os_name.startswith("win"))

        print("✅ Tailscale started.")
        logger.info(f"{session_id} Tailscale start succeeded on {os_name}")
        return True

    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if needs_sudo_retry(stderr, os_name):
            # 2. Пробуем с sudo (если ошибка похожа на "нужен tailscaled")
            try:
                sudo_cmd = ["sudo"] + cmd
                subprocess.run(
                    sudo_cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=False
                )
                print("✅ Tailscale started with sudo.")
                logger.info(f"{session_id} Tailscale sudo-start succeeded on {os_name}")
                return True

            except subprocess.CalledProcessError as sudo_e:
                print("❌ Failed to start Tailscale with sudo:", sudo_e)
                logger.error(
                    f"{session_id} Tailscale sudo start failed. OS: {os_name} "
                    f"STDOUT: {sudo_e.stdout} STDERR: {sudo_e.stderr}",
                    exc_info=True
                )
                return False

        # Если ошибка не связана с tailscaled — не пробуем sudo
        print("❌ Failed to start Tailscale (non-sudo issue):", e)
        logger.error(
            f"{session_id} Tailscale start failed (non-sudo). OS: {os_name} "
            f"STDOUT: {e.stdout} STDERR: {e.stderr}",
            exc_info=True
        )
        return False
    
    except Exception as e:
        print("❌ Unexpected error while starting Tailscale:", e)
        logger.exception("Unexpected error during Tailscale start-up")



import time
import requests
from typing import Optional

from client.config import RFD_IP, RFD_SM_PORT, TAILSCALE_IP_POLL_INTERVAL, TAILSCAPE_IP_TIMEOUT

import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()

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
    

if __name__ == '__main__':
    start_tailscale('test-sess', 'test-auth-key')
import requests
import subprocess

from tech_utils.logger import init_logger
logger = init_logger("Client_Main")

from client.config import CLIENT_TCP_PORT, GCS_TCP_PORT

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
    
import sys
import subprocess
import shutil
import logging


def disconnect():
    from client.gcs_communication.tailscale_connect import is_tailscale_installed, get_tailscale_path, needs_sudo_retry
    if not is_tailscale_installed():
        print("❌ Tailscale is not installed.")
        logger.warning("Tailscale disconnect skipped — not installed.")
        return

    os_name = sys.platform
    ts_path = get_tailscale_path()
    cmd = [ts_path, "down"]
    shell_flag = os_name.startswith("win")

    print("🔌 Disconnecting from Tailnet...")

    # 1. Попытка без sudo
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, shell=shell_flag)
        print("✅ Tailscale VPN disconnected (no sudo).")
        logger.info("Tailscale VPN stopped without sudo")
        return

    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        needs_sudo = needs_sudo_retry(stderr, os_name)

        if needs_sudo:
            try:
                sudo_cmd = ["sudo"] + cmd
                subprocess.run(sudo_cmd, check=True, capture_output=True, text=True)
                print("✅ Tailscale VPN disconnected (with sudo).")
                logger.info("Tailscale VPN stopped with sudo")
                return
            except subprocess.CalledProcessError as sudo_e:
                print("❌ Failed to disconnect Tailscale with sudo:", sudo_e)
                logger.error(
                    f"Tailscale sudo disconnect failed. OS: {os_name} "
                    f"STDOUT: {sudo_e.stdout} STDERR: {sudo_e.stderr}",
                    exc_info=True
                )
        else:
            print("❌ Failed to disconnect Tailscale:", e)
            logger.error(
                f"Tailscale disconnect failed. OS: {os_name} "
                f"STDOUT: {e.stdout} STDERR: {e.stderr}",
                exc_info=True
            )

    except Exception as e:
        print("❌ Unexpected error while disconnecting Tailscale:", e)
        logger.exception("Unexpected error during Tailscale disconnect")


    from client.gcs_communication.tcp_communication import shutdown_client_server
    if not shutdown_client_server():
        print("Could not finish TCP server correctly.")

    return leave()

def leave():
    print("See you next flight!")
    logger.info("Exit the program")
    return True
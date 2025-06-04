import requests
import time
import re

from client.front.config import BACK_SERV_PORT, BACK_POLLING_INTERVAL
from tech_utils.safe_post_req import post_request
from tech_utils.logger import init_logger

logger = init_logger("Front_BCK_Listener")
BASE_URL = f"http://127.0.0.1:{BACK_SERV_PORT}"


def extract_ip(s: str) -> str | None:
    """
    Extracts the first valid IPv4 address found in a string.
    """
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', s)
    return match.group(0) if match else None


def extract_uuid4(text: str) -> str | None:
    """
    Extracts the first UUIDv4 string found in the input text.
    """
    match = re.search(
        r'\b[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b',
        text,
        re.IGNORECASE
    )
    return match.group(0) if match else None

def back_polling():
    """
    Polls the backend periodically for status updates and events.

    Responds to:
      - 'abort' or 'finish' commands (sets corresponding events)
      - 'session-request' messages (extracts GCS IP and session ID)
      - Tailscale connection updates
      - General backend messages

    Also handles automatic session closure if finish/abort is received.
    """
    from client.front.state import front_state

    while front_state.poll_back_event.is_set():
        try:
            res = requests.post(url=BASE_URL+"/get-message", json={}, timeout=3)
            if res.status_code == 200:
                message = res.json().get('message')
                if message == "abort":
                    logger.info("Abort command received from backend.")
                    front_state.abort_event.set()
                    post_request(
                        url=f"{BASE_URL}/front-close-session",
                        payload={"result": "abort"},
                        description="Front2Back: abort session"
                    )

                elif message == "finish":
                    logger.info("Finish command received from backend.")
                    front_state.finish_event.set()
                    post_request(
                        url=f"{BASE_URL}/front-close-session",
                        payload={"result": "finish"},
                        description="Front2Back: finish session"
                    )

                elif message.startswith("session-request"):
                    front_state.main_screen.append_log(f"👋 GCS {extract_ip(message)} requests a session.\Click 'launch' to start or 'abort' to cancel it")
                    front_state.session_id = extract_uuid4(message)

                elif message.startswith("ts-connected"):
                    front_state.tailscale_connected_event.set()
                    front_state.tailscale_disconnect_event.set() # To give time for event waiter to release execution
                    time.sleep(0.2) # To give time for event waiter to release execution
                    front_state.tailscale_disconnect_event.clear()
                    front_state.main_screen.append_log(" ".join(message.split(" ")[1:]))

                elif message.startswith("ts-disconnected"):
                    front_state.tailscale_disconnect_event.set()
                    front_state.tailscale_connected_event.set() # To give time for event waiter to release execution
                    time.sleep(0.2) # To give time for event waiter to release execution
                    front_state.tailscale_connected_event.clear()
                    front_state.main_screen.append_log(" ".join(message.split(" ")[1:]))

                else:
                    front_state.main_screen.append_log(message)

        except Exception as e:
            logger.warning(f"Polling exception: {e}")
            time.sleep(2)

        time.sleep(BACK_POLLING_INTERVAL)
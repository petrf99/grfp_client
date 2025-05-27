from client.front.config import BACK_SERV_PORT, BACK_POLLING_INTERVAL
import requests
import time

from tech_utils.safe_post_req import post_request
from flask import request

BASE_URL = f"http://127.0.0.1:{BACK_SERV_PORT}"

import re
def extract_ip(s: str):
    match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', s)
    return match.group(0) if match else None

def extract_uuid4(text: str) -> str | None:
    match = re.search(r'\b[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b', text, re.IGNORECASE)
    return match.group(0) if match else None



from tech_utils.logger import init_logger
logger = init_logger("Front_BCK_Listener")

def back_polling():
    from client.front.state import front_state
    global BASE_URL
    while front_state.poll_back_event.is_set():
        try:
            res = requests.post(url=BASE_URL+"/get-message", json={}, timeout=3)
            if res.status_code == 200:
                message = res.json().get('message')
                if message == "finish" or message == "abort":
                    logger.info(f"{message} command received from Back-end")
                    if message == 'abort':
                        front_state.abort_event.set()
                    else:
                        front_state.finish_event.set()

                    result = message
                    res = post_request(url = f"{BASE_URL}/front-close-session", payload={"result": result},
                                 description=f"Front2Back: {result} session")
                elif message.startswith("session-request"):
                    print(f"\n👋 GCS {extract_ip(message)} requests a session.\nType 'launch' to start or 'abort' to cancel it")
                    front_state.session_id = extract_uuid4(message)
                elif message.startswith("ts-connected"):
                    front_state.tailscale_connected_event.set()
                    print(" ".join(message.split(" ")[1:]))
                elif message.startswith("ts-disconnected"):
                    front_state.tailscale_connected_event.set()
                    time.sleep(0.01)
                    front_state.tailscale_connected_event.clear()
                    print(" ".join(message.split(" ")[1:]))
                else:
                    print(message)

        except Exception as e:
            pass

        time.sleep(BACK_POLLING_INTERVAL)

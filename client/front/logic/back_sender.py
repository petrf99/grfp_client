import requests
import time

from client.front.config import CLIENT_BACK_SERV_PORT
from client.front.logic.back_listener import sess_state

from tech_utils.logger import init_logger
logger = init_logger("Front_BCK_Sender")

def close_session(session_id = None, finish_flg = False):
    json={"finish_flg": finish_flg}
    if session_id:
        json["session_id"] = session_id
    try:
        response = requests.post(f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/close-session", json=json, timeout=5)
        data = response.json()
        if response.status_code == 200:
            if data.get("status") == "ok":
                logger.info(f"Session-id:{session_id} close-session command sent")
                sess_state.clear()
                return True
        else:
            logger.info(f"Can't send close-session command to back. Reason: {data.get('reason', '')}\n")
            sess_state.clear()
            return False
    except Exception as e:
        logger.error("Close session: Could not reach Backend\n")
        sess_state.clear()
        return False
    
def shutdown():
    try:
        response = requests.post(f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/shutdown", json={}, timeout=5)
        data = response.json()
        if response.status_code == 200:
            if data.get("status") == "ok":
                logger.info(f"Shutdown command sent")
                sess_state.clear()
                return True
        else:
            logger.info(f"Can't send shutdown command to back. Reason: {data.get('reason', '')}\n")
            sess_state.clear()
            return False
    except Exception as e:
        logger.error(f"Shutdown: Could not reach Backend {e}\n")
        sess_state.clear()
        return False

def start_session(session_id):
    json={"session_id": session_id}
    try:
        response = requests.post(f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/start-session", json=json, timeout=5)
        data = response.json()
        if response.status_code == 200:
            if data.get("status") == "ok":
                logger.info(f"Session-id: {session_id} start-session command sent")
                return True
        else:
            logger.info(f"Can't send start-session command to back. Reason: {data.get('reason', '')}")
            return False
    except Exception as e:
        logger.error("Start session: Could not reach Backend\n")
        return False

def launch_streams(session_id, controller):
    json={"session_id": session_id, "controller": controller}
    try:
        response = requests.post(f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/launch-streams", json=json, timeout=5)
        data = response.json()
        if response.status_code == 200:
            if data.get("status") == "ok":
                logger.info(f"Session-id: {session_id} launch-streams command sent sucessfully")
                return True
        else:
            logger.info(f"Can't send launch-streams command to back. Reason: {data.get('reason', '')}\n")
            return False
    except Exception as e:
        logger.error("Launch streams: Could not reach Backend\n")
        return False

def token_validator(token):
    try:
        response = requests.post(f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/validate-token", json={"token": token}, timeout=5)
        data = response.json()
        if response.status_code == 200:
            if data.get("status") == "ok" and "session_id" in data:
                logger.info(f"Token verified successully. Session-id:\n{data['session_id']}\n")
                return data["session_id"]
        else:
            logger.info(f"Token verification failed. Reason: {data.get('reason', '')}\n")
            return False
    except Exception as e:
        logger.error("Token validator: Could not reach Backend\n")
        return False


import json
import time

from client.front.config import UDP_SEND_LOG_DELAY, GCS_RC_RECV_PORT

from tech_utils.udp import get_socket
sock = get_socket()

_last_log_map = {}
def send_rc_frame(sock, session_id, rc_state, source):
    global _last_log_map
    now = time.time()
    json_data = json.dumps(rc_state).encode('utf-8')

    try:
        sock.sendto(json_data, ("127.0.0.1", GCS_RC_RECV_PORT))
        last = _last_log_map.get(session_id, 0)
        if now - last >= UDP_SEND_LOG_DELAY:
            logger.info(f"Frame sent to 127.0.0.1:{GCS_RC_RECV_PORT} JSON:{rc_state}")
            _last_log_map[session_id] = now
    except Exception as e:
        logger.error(f"Exception occurred while sending UDP: {e}", exc_info=True)
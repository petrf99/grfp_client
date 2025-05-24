from tech_utils.logger import init_logger
logger = init_logger("Front_TKN_VLDTR")

import requests

from client.config import RFD_IP, RFD_SM_PORT

import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()

RFD_URL = f"http://{RFD_IP}:{RFD_SM_PORT}/validate-token"

def validate_token(token):
    try:
        response = requests.post(RFD_URL, json={"token": hash_token(token)}, timeout=5)
        data = response.json()
        if response.status_code == 200:
            if data.get("status") == "ok" and "session_id" in data:
                logger.info(f"Token with hash {hash_token(token)} verified successully. Session-id:\n{data['session_id']}\n")
                return data["session_id"]
        else:
            logger.info(f"Token with hash {hash_token(token)} verification failed. Reason: {data.get('reason', '')}\n")
            return False
    except Exception as e:
        logger.error("Could not reach RFD\n")
        return False
import requests

from tech_utils.logger import init_logger
logger = init_logger("RCClientAuth")

from client.config import RFD_IP, RFD_SM_PORT, TOKEN_VAL_METHOD

RFD_URL = f"http://{RFD_IP}:{RFD_SM_PORT}/{TOKEN_VAL_METHOD}"  
print(RFD_URL)


# В начале твоего auth.py или main.py — только на время разработки:
from unittest.mock import patch, Mock

def mock_post(url, json, timeout):
    print(f"[MOCK] Called mock_post with token: {json['token']}")
    if json['token'] == "test123":
        return Mock(status_code=200, json=lambda: {"status": "ok", "session_id": "mock-session-xyz"})
    else:
        return Mock(status_code=403, json=lambda: {"status": "error"})


import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()


def get_valid_token():
    print("\nWelcome to Genesis Remote Flights Platform ✈️")
    
    while True:
        token = input("Please enter your Mission Access Token (or enter 'leave' to exit the program): ").strip()
        if token == 'leave':
            return False
        logger.info(f"Token entered: {token}")

        try:
            # with patch("requests.post", new=mock_post):
            response = requests.post(RFD_URL, json={"token": hash_token(token)}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok" and "session_id" in data:
                    print("✅ Token verified successfully.")
                    logger.info(f"Token {token} verified successully. Session-id:\n{data['session_id']}\n")
                    return token, data["session_id"]
            else:
                logger.info(f"Token {token} verification failed\n")
                print("❌ Invalid token. Please try again.")
        except Exception as e:
            print(f"⚠️ Could not reach RFD: {e}")
            logger.error("Could not reach RFD\n")
            print("Retrying...")

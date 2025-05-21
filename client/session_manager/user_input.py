import requests
from tech_utils.logger import init_logger
logger = init_logger("Client_Main")

from client.session_manager.basic_commands import leave, close, disconnect

from client.config import RFD_IP, RFD_SM_PORT

import hashlib
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest().upper()

RFD_URL = f"http://{RFD_IP}:{RFD_SM_PORT}/validate-token"

def enter_token():
    print("\nWelcome to Genesis Remote Flights Platform ✈️")
    print("\nPlease enter your Mission Access Token (or enter 'leave' to exit the program):")
    
    try:
        while True:
            token = input().strip()
            if token == 'leave':
                return False
            logger.info(f"Token entered. Hash: {hash_token(token)}")

            try:
                response = requests.post(RFD_URL, json={"token": hash_token(token)}, timeout=5)
                data = response.json()
                if response.status_code == 200:
                    if data.get("status") == "ok" and "session_id" in data:
                        print("✅ Token verified successfully.")
                        logger.info(f"Token with hash {hash_token(token)} verified successully. Session-id:\n{data['session_id']}\n")
                        return token, data["session_id"]
                else:
                    logger.info(f"Token with hash {hash_token(token)} verification failed. Reason: {data.get('reason', '')}\n")
                    print(f"❌ Token verification failed. Reason: {data.get('reason', '')}")
            except Exception as e:
                print(f"⚠️ Could not reach RFD: {e}")
                logger.error("Could not reach RFD\n")
                print("Retrying...")
    except KeyboardInterrupt:
        logger.warning("User interrupted during enter_token(). Aborting session.")
        leave()
        return None

def ready():
    print("\nIf you are ready to fly, please type 'ready'.\nOr type 'abort' to terminate the process.")
    try:
        while True:
            cmd = input().strip().lower()
            logger.info(f"Command <{cmd}> received from user")
            if cmd == 'ready':
                return True
            elif cmd == 'abort':
                return False
            else:
                print("Please type 'ready' or 'abort'")
    except KeyboardInterrupt:
        logger.warning("User interrupted during ready(). Aborting session.")
        leave()
        return None


from client.config import CONTROLLERS_LIST

def select_controller():
    print("\nPlease select your controller:\n1 - keyboard\n2 - mouse+keyboard\n3 - gamepad\n4 - drone remote controller\n\nIf you want to terminate the process type 'abort'")

    try:
        while True:
            try:
                inp = input()
                logger.info(f"Controller type {inp} received from user")
                if inp == 'abort':
                    return False
                controller_type = int(inp)
                if controller_type >= 1 and controller_type <= len(CONTROLLERS_LIST):
                    controller = CONTROLLERS_LIST[controller_type-1]
                    logger.info(f"Controller {controller} is chosen")
                    return controller
                else:
                    print(f"Please enter a number 1-{len(CONTROLLERS_LIST)}:")
            except:
                print(f"Please enter a number 1-{len(CONTROLLERS_LIST)}:")
    except KeyboardInterrupt:
        logger.warning("User interrupted during select_controller(). Aborting session.")
        leave()
        return None
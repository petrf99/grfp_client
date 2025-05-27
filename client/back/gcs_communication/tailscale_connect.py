from tech_utils.logger import init_logger
logger = init_logger("Client_Tailscale_Connect")


from cryptography.hazmat.primitives import serialization
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from tech_utils.rsa_keys_gen import generate_keys_if_needed

from tech_utils.safe_post_req import post_request

from client.back.front_communication.front_msg_sender import send_message_to_front

from client.back.config import RFD_IP, RFD_SM_PORT
from client.back.state import client_state
from tech_utils.tailscale import tailscale_up

# === Tailscale up ===

def connect(mission_id):
    client_state.mission_id = mission_id
    if not get_vpn_connection():
        send_message_to_front("ts-disconnected: ❌ Tailscale connect failed")
        return False

    return start_tailscale()

def start_tailscale():
    if not tailscale_up(client_state.hostname, client_state.token):
        send_message_to_front("ts-disconnected: ❌ Tailscale connect failed")
        return False
    
    send_message_to_front("ts-connected: ✅ Tailscale connected")
    return True


# === Get connection via RFD ===
from client.back.config import RFD_IP, RFD_SM_PORT, ABORT_MSG, FINISH_MSG
RFD_URL = f"http://{RFD_IP}:{RFD_SM_PORT}"

RFD_CONNECT_URL = RFD_URL + "/get-vpn-connection"  

from client.back.config import RSA_PRIVATE_PEM_PATH, RSA_PUBLIC_PEM_PATH
def get_vpn_connection():
    send_message_to_front("Requesting VPN credentials from Remote Flights Dispatcher...")
    logger.info(f"Sending get-vpn-connection request to RFD")

    logger.info("Generate RSA keys")
    generate_keys_if_needed(RSA_PRIVATE_PEM_PATH, RSA_PUBLIC_PEM_PATH)


    with open(RSA_PUBLIC_PEM_PATH, "rb") as f:
        public_pem = f.read()

    payload = {
        "tag": "client",
        "rsa_pub_key": public_pem.decode('utf-8'),
        "mission_id": client_state.mission_id
    }

    res = post_request(RFD_CONNECT_URL, payload, "Client get-vpn-connection")
    if res:
        with open(RSA_PRIVATE_PEM_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        client_state.token = private_key.decrypt(
            base64.b64decode(res.get("token")),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        ).decode()

        client_state.hostname = res.get("hostname")
        client_state.token_hash = res.get("token_hash")
        send_message_to_front(f"✅ VPN credentials obtained.")
        logger.info(f"get-vpn-connection succeed. Hostname: {client_state.hostname}. Token_hash: {client_state.token_hash}. Token: {client_state.token[-10:]}")
    else:
        send_message_to_front(f"❌ Can't obtain VPN credentials. Please contact admin")
        logger.error(f"get-vpn-connection failed.")

    return res is not None


RFD_DELETE_CONN_URL = RFD_URL + "/delete-vpn-connection"  
def delete_vpn_connection():
    send_message_to_front("Deleting VPN credentials from Remote Flights Dispatcher...")
    logger.info(f"Sending delete-vpn-connection request to RFD")

    payload = {
        "hostname": client_state.hostname,
        "token_hash": client_state.token_hash
    }

    res = post_request(RFD_DELETE_CONN_URL, payload, "Client delete-vpn-connection")
    if res:
        send_message_to_front(f"✅ VPN credentials deleted from RFD.")
        logger.info(f"delete-vpn-connection succeed. Hostname: {client_state.hostname}. Token_hash: {client_state.token_hash}.")
    else:
        send_message_to_front(f"❌ Can't delte VPN credentials from RFD. Please contact admin")
        logger.error(f"delete-vpn-connection failed.")

    return res is not None
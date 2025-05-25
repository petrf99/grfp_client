import os
from dotenv import load_dotenv

load_dotenv()

# === Настройки ===
RFD_IP = os.getenv("RFD_IP")       # адрес сервера RFD
RFD_SM_PORT = int(os.getenv("RFD_SM_PORT"))           
TOKEN_VAL_METHOD = os.getenv("TOKEN_VAL_METHOD")

# === Tailscale connect to gcs ===
TAILSCALE_IP_POLL_INTERVAL = 3
TAILSCAPE_IP_TIMEOUT = 600
GCS_TCP_PORT = int(os.getenv("GCS_TCP_PORT"))
CLIENT_TCP_PORT = int(os.getenv("CLIENT_TCP_PORT"))
NUM_START_SESS_ATTEMPTS=150
START_SESS_POLL_INTERVAL=2

TCP_KEEP_CONNECTION_RETRIES=3
PING_INTERVAL=1

# === UDP GCS-Client params ===
CLIENT_VID_RECV_PORT=int(os.getenv("CLIENT_VID_RECV_PORT"))
CLIENT_TLMT_RECV_PORT=int(os.getenv("CLIENT_TLMT_RECV_PORT"))
GCS_RC_RECV_PORT=int(os.getenv("GCS_RC_RECV_PORT"))
UDP_SEND_LOG_DELAY = 3

# === Константы каналов ===
RC_CHANNELS_DEFAULTS = {
    "ch1": 1500,  # roll (← →)
    "ch2": 1500,  # pitch (↑ ↓)
    "ch3": 1000,  # throttle (W/S)
    "ch4": 1500,  # yaw (A/D)
    "ch5": 1000,  # arm/disarm (Space)
    "ch6": 1000,   # aux (Shift)
    "ch7": 1000,
    "ch8": 1000,
    "ch9": 1000,
    "ch10": 1000,
    "ch11": 1000,
    "ch12": 1000,
    "ch13": 1000,
    "ch14": 1000,
    "ch15": 1000,
    "ch16": 1000,
}

# Controllers list
CONTROLLERS_LIST = ['keyboard', 'mouse_keyboard', 'gamepad', 'drone_radio']
BACKEND_CONTROLLER = ['gamepad', 'drone_radio']

# Local ports
CLIENT_BACK_SERV_PORT=int(os.getenv("CLIENT_BACK_SERV_PORT"))
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
GCS_UDP_PORT=int(os.getenv("GCS_UDP_PORT"))
CLIENT_UDP_PORT=int(os.getenv("GCS_UDP_PORT"))

# === Константы каналов ===
RC_CHANNELS_DEFAULTS = {
    "ch1": 1500,  # roll (← →)
    "ch2": 1500,  # pitch (↑ ↓)
    "ch3": 1000,  # throttle (W/S)
    "ch4": 1500,  # yaw (A/D)
    "ch5": 1000,  # arm/disarm (Space)
    "ch6": 1000   # aux (Shift)
}

# Controllers list
CONTROLLERS_LIST = ['keyboard', 'mouse_keyboard', 'gamepad', 'drone_radio']

# Keyboard params
STEP_ANALOG = 20      # шаг изменения каналов
LIMIT_MIN = 1000
LIMIT_MAX = 2000

# Main loop
FREQUENCY = 20
UDP_SEND_LOG_DELAY = 1

# GUI
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
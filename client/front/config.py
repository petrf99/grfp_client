import os
from dotenv import load_dotenv

load_dotenv()


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

# Keyboard params
STEP_ANALOG = 20      # шаг изменения каналов
LIMIT_MIN = 1000
LIMIT_MAX = 2000

# Main loop
FREQUENCY = 25

# GUI
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TELEMETRY_GUI_DRAW_FIELDS=["timestamp", "rc_channels"]
NO_FRAME_MAX = 50

# Local settings
BACK_SERV_PORT=int(os.getenv("BACK_SERV_PORT"))
BACK_POLLING_INTERVAL=0.5

HELP_FILE_PATH="client/settings/help.txt"
CONTROLLER_PATH="client/settings/controller.txt"

BACKEND_CONTROLLER = ['gamepad', 'rc_controller']
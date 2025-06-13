import os
import json
from client.front.config import *
from client.front.inputs import get_rc_input

import threading

from tech_utils.logger import init_logger
logger = init_logger(name="State", component="front")

class FrontState:
    def __init__(self):
        self.session_id = None
        self.active_mission = None
        self.tailscale_connected_event = threading.Event()
        self.tailscale_disconnect_event = threading.Event()
        self.poll_back_event = threading.Event()

        self.email = None
        self.jwt = None
        
        self.running_event = threading.Event()

        self.login_screen = None
        self.main_screen = None
        self.flight_screen = None

        self.controller = None
        self.rc_input = None
        # Controller params
        self.sensitivity = 1
        self.deadzone = 0
        self.expo = 0.0
        self._load_controller_config()
        self.set_controller()

    def set_controller(self, controller = None):
        from client.front.inputs import DeviceManager
        if controller and controller in DeviceManager.short_names() + BASE_CONTROLLERS_LIST:
            self.controller = controller
        elif controller:
            logger.error("Invalid controller in set_controller")
            return False
        params = {"sensitivity": self.sensitivity, "expo": self.expo, "deadzone": self.deadzone}
        self.rc_input = None if self.controller in BACKEND_CONTROLLER else get_rc_input(self.controller, params)
        return True

    def _load_controller_config(self):
        """
        Load controller preference from JSON file or write default if not found.
        """
        if os.path.exists(CONTROLLER_PATH):
            with open(CONTROLLER_PATH, "r") as f:
                try:
                    config = json.load(f)
                    controller_name = config.get("controller")
                    if controller_name in BASE_CONTROLLERS_LIST:
                        self.controller = controller_name
                    self.sensitivity = float(config.get("sensitivity", self.sensitivity))
                    self.expo = float(config.get("expo", self.expo))
                    self.deadzone = config.get("deadzone", self.deadzone)
                except (json.JSONDecodeError, ValueError):
                    logger.warning("⚠️ Failed to load controller settings: Incorrect JSON. Use defaults.")
        else:
            os.makedirs(os.path.dirname(CONTROLLER_PATH), exist_ok=True)

        # Если контроллер всё ещё None — пишем по умолчанию
        if self.controller is None:
            self.controller = DEFAULT_CONTROLLER
            config = {
                "controller": self.controller,
                "sensitivity": self.sensitivity,
                "expo": self.expo,
                "deadzone": self.deadzone
            }
            with open(CONTROLLER_PATH, "w") as f:
                json.dump(config, f, indent=2)



    def clear(self):
        self.session_id = None
        self.running_event.clear()
    def status(self):
        return f"Session ID: {self.session_id}\nVPN Connected: {self.tailscale_connected_event.is_set()}"


front_state = FrontState()
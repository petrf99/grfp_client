import os
from client.front.config import *
from client.front.inputs import get_rc_input

import threading

class FrontState:
    def __init__(self):
        self.session_id = None
        self.active_mission = None
        self.tailscale_connected_event = threading.Event()
        self.tailscale_disconnect_event = threading.Event()
        self.poll_back_event = threading.Event()

        self.user_id = None

        self.abort_event = threading.Event()
        self.finish_event = threading.Event()

        self.login_screen = None
        self.main_screen = None
        self.flight_screen = None

        self.controller = None
        self._load_controller_config()
        self.rc_input = None if self.controller in BACKEND_CONTROLLER else get_rc_input(self.controller)

    def _load_controller_config(self):
        """
        Load controller preference from disk or write default if not found.
        """
        if os.path.exists(CONTROLLER_PATH):
            with open(CONTROLLER_PATH, "r") as f:
                controller_name = f.read().strip()
                if controller_name in CONTROLLERS_LIST:
                    self.controller = controller_name
        else:
            os.makedirs(os.path.dirname(CONTROLLER_PATH), exist_ok=True)

        if self.controller is None:
            with open(CONTROLLER_PATH, "w") as f:
                f.write(DEFAULT_CONTROLLER)
            self.controller = DEFAULT_CONTROLLER

    def clear(self):
        self.session_id = None
        self.abort_event.clear()
        self.finish_event.clear()

    def status(self):
        return f"Session ID: {self.session_id}\nVPN Connected: {self.tailscale_connected_event.is_set()}"


front_state = FrontState()
import threading
import os

from client.back.config import (
    CLIENT_TLMT_RECV_PORT,
    CLIENT_VID_RECV_PORT,
    CONTROLLERS_LIST,
    DEFAULT_CONTROLLER,
    CONTROLLER_PATH
)


class SessionState:
    """
    This class holds the current session state for the Client backend.

    It tracks session identity, port assignments, connection state,
    cryptographic credentials, and controller selection.
    """
    
    def __init__(self):
        # === Session identifiers ===
        self.session_id = None
        self.mission_id = None

        # === Thread control events ===
        self.finish_event = threading.Event()
        self.abort_event = threading.Event()
        self.external_stop_event = threading.Event()

        # === Client network ports for receiving telemetry and video ===
        self.client_vid_port = CLIENT_VID_RECV_PORT
        self.client_tlmt_port = CLIENT_TLMT_RECV_PORT

        # === GCS connection parameters ===
        self.gcs_ip = None
        self.gcs_rc_port = None

        # === VPN authentication credentials (Tailscale) ===
        self.token = None
        self.hostname = None
        self.token_hash = None

        # === Session mode (e.g., "rfp", "e2e") ===
        self.mode = None

        # === Controller configuration ===
        self.controller = None
        self._load_controller_config()

        # === Signal to stop the backend thread from frontend ===
        self.stop_back_event = threading.Event()

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
        """
        Reset all session-specific fields to prepare for a new session.
        """
        self.session_id = None
        self.mission_id = None

        self.finish_event.clear()
        self.abort_event.clear()
        self.external_stop_event.clear()

        self.client_vid_port = CLIENT_VID_RECV_PORT
        self.client_tlmt_port = CLIENT_TLMT_RECV_PORT

        self.gcs_ip = None
        self.gcs_rc_port = None

        self.token = None
        self.hostname = None
        self.token_hash = None

        self.mode = None

    def __str__(self):
        return f"Session: {self.session_id}. Mission: {self.mission_id}"


# === Global session state instance ===
client_state = SessionState()

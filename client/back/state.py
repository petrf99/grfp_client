import threading
import os

from client.back.config import CLIENT_TLMT_RECV_PORT, CLIENT_VID_RECV_PORT, CONTROLLERS_LIST, DEFAULT_CONTROLLER, CONTROLLER_PATH

class SessionState:
    def __init__(self):
        self.session_id = None
        self.mission_id = None

        self.finish_event = threading.Event()
        self.abort_event = threading.Event()
        self.external_stop_event = threading.Event()

        self.client_vid_port = CLIENT_VID_RECV_PORT
        self.client_tlmt_port = CLIENT_TLMT_RECV_PORT

        self.gcs_ip = None
        self.gcs_rc_port = None

        self.token = None
        self.hostname = None
        self.token_hash = None

        self.mode = None

        self.controller = None
        if os.path.exists(CONTROLLER_PATH):
            with open(CONTROLLER_PATH, "r") as f:
                if f.read() in CONTROLLERS_LIST:
                    self.controller = f.read()
        else:
            os.makedirs(os.path.dirname(CONTROLLER_PATH), exist_ok=True)
        if self.controller is None:
            with open(CONTROLLER_PATH, "w") as f:
                f.write(DEFAULT_CONTROLLER)
                self.controller = DEFAULT_CONTROLLER

        self.running = threading.Event()

    def __str__(self):
        return f"Session: {self.session_id}. Mission: {self.mission_id}"
    
    def clear(self):
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


client_state = SessionState()
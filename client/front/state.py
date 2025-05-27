from client.front.logic.input_handlers import *

step_handlers = {
    "greeting": step_greeting,
    "mission_id_input": step_mission_id_input,
    "done": step_done,
    "free_input": step_free_input
}

import threading

class FrontState:
    def __init__(self):
        self.session_id = None
        self.tailscale_connected_event = threading.Event()
        self.poll_back_event = threading.Event()

        self.abort_event = threading.Event()
        self.finish_event = threading.Event()

    def clear(self):
        self.session_id = None
        self.abort_event.clear()
        self.finish_event.clear()


front_state = FrontState()
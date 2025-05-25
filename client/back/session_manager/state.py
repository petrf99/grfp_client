import threading

class SessionState:
    def __init__(self):
        self.finish_event = threading.Event()
        self.abort_event = threading.Event()
        self.external_stop_event = threading.Event()
        self.controller = ''
        self.session_id = ''
        self.auth_token = ''
        self.mission_id = ''
        self.gcs_ip = ''

    def clear(self):
        self.__init__()


sess_state = SessionState()
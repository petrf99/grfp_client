import uuid 
from tech_utils.logger import init_logger
from client.front.config import CONTROLLERS_LIST

from client.front.logic.back_sender import start_session, close_session, launch_streams, token_validator
from client.front.gui.gui_loop import gui_loop
from client.front.inputs import get_rc_input

logger = init_logger("Front_Main")

class FrontState:
    def __init__(self):
        self.session_id = None
        self.start_flg = False
        self.val_token_flg = False
        self.sess_start_flg = False
        self.contr_sel_flg = False
        self.ready_flg = False
        self.controller = None
        self.rc_input = None

    def clear(self):
        self.__init__()

state = FrontState()


def handle_token_input(state, cmd):
    session_id = token_validator(cmd)
    try:
        uuid.UUID(session_id)
        state.session_id = session_id
        state.val_token_flg = True
        logger.info(f"Token validated successfully: {session_id}")
        print("Token verification succeeded.")
        return True
    except:
        logger.warning("Token validation failed.")
        print("Token validation failed.")
        state.session_id = None
        return False

from client.front.logic.back_listener import sess_state
def handle_session_start(state):
    state.sess_start_flg = start_session(state.session_id)
    if state.sess_start_flg:
        print("Session is being started. Please wait.\nYou may be asked to enter password in order to run Tailscale")
        sess_state.connected_event.wait()
        logger.info(f"Session {state.session_id} started.")
        return True
    else:
        print("Unable to start session.")
        logger.error("Session start failed.")
        close_session(state.session_id)
        state.reset()
        print("Session stopped. You can start a new one by typing 'start'")
        return False


def handle_controller_selection(state, cmd):
    try:
        controller = CONTROLLERS_LIST[int(cmd) - 1]
    except:
        controller = None

    if controller:
        state.controller = controller
        state.rc_input = get_rc_input(controller)
        logger.info(f"Controller selected: {controller}")
        print("Controller registered. Type 'ready' to start your flight or 'abort'.")
        state.ready_flg = True
        return True
    else:
        print(f"Invalid controller. Please enter a number 1-{len(CONTROLLERS_LIST)}.")
        return False


def launch_session(state):
    finish_flg = False
    if not launch_streams(state.session_id, state.controller):
        print("Failed streams launch")
    else:
        logger.info("Streams launched. Starting GUI loop...")
        finish_flg = gui_loop(state.session_id, state.rc_input, state.controller)
        logger.info(f"Session completed and stopped with finish_flg {finish_flg}.")
    if not sess_state.external_stop_event.is_set():
        print("Flight session stopped.")
    close_session(state.session_id, finish_flg=finish_flg)
    state.clear()
    sess_state.clear()
    return finish_flg
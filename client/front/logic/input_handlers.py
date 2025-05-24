from uuid import UUID
from tech_utils.timed_input import timed_input
from tech_utils.logger import init_logger
from client.config import CONTROLLERS_LIST

from client.front.logic.token_validator import validate_token
from client.front.logic.back_interaction import start_session, stop, launch_streams
from client.front.gui.gui_loop import gui_loop
from client.inputs import get_rc_input

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

    def reset(self):
        self.__init__()


def handle_token_input(state, cmd):
    session_id = validate_token(cmd)
    if isinstance(session_id, UUID):
        state.session_id = session_id
        state.val_token_flg = True
        logger.info(f"Token validated successfully: {session_id}")
        print("Token verification succeeded.")
    else:
        logger.warning("Token validation failed.")
        print("Token validation failed.")
        state.session_id = None


def handle_session_start(state):
    state.sess_start_flg = start_session(state.session_id)
    if state.sess_start_flg:
        logger.info(f"Session {state.session_id} started.")
    else:
        print("Unable to start session.")
        logger.error("Session start failed.")
        stop(state.session_id)
        state.reset()
        print("Session stopped. You can start a new one by typing 'start'")


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
    else:
        print(f"Invalid controller. Please enter a number 1-{len(CONTROLLERS_LIST)}.")


def launch_session(state):
    launch_streams(state.session_id)
    logger.info("Streams launched. Starting GUI loop...")
    gui_loop(state.session_id, state.rc_input, state.controller)
    stop(state.session_id, finish_flg=True)
    logger.info("Session completed and stopped.")
    print("Flight session finished.")
    state.reset()
from tech_utils.timed_input import timed_input
from tech_utils.logger import init_logger

from client.front.logic.input_handlers import FrontState, handle_controller_selection, handle_session_start, handle_token_input, launch_session
from client.front.logic.back_sender import stop

logger = init_logger("Front_Main")



def main():
    logger.info("Program started.")
    print("\nWelcome to Genesis Remote Flights Platform ✈️")
    print("Enter 'start' to begin or 'exit'/'leave' to exit the program.")

    state = FrontState()

    try:
        while True:
            cmd = timed_input()
            logger.info(f"Command received: {cmd}")

            if cmd is None:
                continue

            if cmd in ["exit", "leave"]:
                if state.session_id:
                    stop(state.session_id)
                else:
                    stop()
                print("See you next flight!")
                logger.info("Program exited by user.")
                return

            if cmd == "abort":
                logger.info("Abort command received.")
                if state.session_id:
                    print(f"Stopping session {state.session_id}...")
                    stop(state.session_id)
                else:
                    print("No session to stop.")
                sid = state.session_id
                state.reset()
                print(f"Session {sid} stopped. Type 'start' to begin a new session.")
                continue

            if cmd == "start" and not state.start_flg:
                state.start_flg = True
                logger.info("Session start initiated.")
                print("Enter your Mission Access Token (or type 'exit' to cancel):")
                continue

            if state.start_flg and not state.val_token_flg:
                handle_token_input(state, cmd)
                if not state.val_token_flg:
                    continue
                handle_session_start(state)
                if not state.sess_start_flg:
                    continue
                print("Select your controller:")
                print("1 - keyboard\n2 - mouse+keyboard\n3 - gamepad\n4 - drone remote controller")
                print("Type 'abort' to cancel.")
                state.contr_sel_flg = True
                continue

            if state.contr_sel_flg and not state.ready_flg:
                handle_controller_selection(state, cmd)
                continue

            if state.ready_flg:
                if cmd == "ready":
                    logger.info(f"User confirmed ready for session {state.session_id}.")
                    launch_session(state)
                else:
                    print("Please type 'ready' to begin or 'abort' to cancel.")
                continue

            print("Unknown command.")

    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received.")
        if state.session_id:
            stop(state.session_id)
        else:
            stop()
        print("\nSession terminated. See you next flight!")




if __name__ == "__main__":
    main()


from tech_utils.timed_input import timed_input
from tech_utils.logger import init_logger

from client.front.logic.input_handlers import handle_controller_selection, handle_session_start, handle_token_input, launch_session
from client.front.logic.back_sender import close_session, shutdown
from client.front.logic.back_listener import back_polling, sess_state
from client.front.logic.input_handlers import state

import threading

logger = init_logger("Client_Front_Main")



def main():
    logger.info("Program started.")
    print("\nWelcome to the Remote Flights Platform ✈️")
    print("Enter 'start' to begin or 'exit'/'leave' to exit the program.")


    # Запускаем поллинг бэкенда в отдельном потоке
    bp = threading.Thread(target=back_polling, daemon=True)
    bp.start()

    try:
        while True:
            cmd = timed_input()

            if cmd is None:
                continue
            
            if not state.start_flg:
                logger.info(f"Command received: {cmd}")

            if cmd in ["exit", "leave"]:
                if state.session_id:
                    close_session(state.session_id)
                shutdown()
                print("See you next flight!")
                logger.info("Program exited by user.")
                return

            if cmd == "abort":
                logger.info("Abort command received.")
                if not sess_state.abort_event.is_set():
                    sess_state.abort_event.set()
                if state.session_id:
                    print(f"Abort command received. Stopping session {state.session_id}...")
                    close_session(state.session_id)
                else:
                    print("No session to stop.")
                sid = state.session_id
                state.clear()
                sess_state.clear()
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
            close_session(state.session_id)
        shutdown()
        print("\nSession terminated. See you next flight!")
    finally:
        bp.join()




if __name__ == "__main__":
    main()


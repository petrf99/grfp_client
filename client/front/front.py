from client.front.state import front_state
from PySide6.QtWidgets import QApplication, QStackedWidget
from client.front.login_screen.login_class import LoginScreen
from client.front.main_screen.main_class import MainScreen
from client.front.flight_screen.fs_class import FlightScreen
from client.front.config import BACK_SERV_PORT
import time
import threading
from client.front.logic.back_listener import back_polling
from tech_utils.safe_post_req import post_request
from tech_utils.logger import init_logger

logger = init_logger("Front_Main")

def main():
    logger.info("Starting frontend")

    app = QApplication([])
    stack = QStackedWidget()

    # Initialize screens
    front_state.login_screen = LoginScreen(stack)
    front_state.main_screen = MainScreen(stack)
    front_state.flight_screen = FlightScreen(stack)

    # Add screens to stack
    stack.addWidget(front_state.login_screen)  # index 0
    stack.addWidget(front_state.main_screen)   # index 1
    stack.addWidget(front_state.flight_screen)  # index 2

    stack.setCurrentIndex(0)  # Login screen

    stack.setWindowTitle("Remote Flights Platform")
    stack.resize(800, 600)
    stack.show()

    logger.info(f"QApp initialized and set up. Stack len: {stack.count()}")

    # Start background polling thread for back-end updates
    bp = threading.Thread(target=back_polling, daemon=True)
    front_state.poll_back_event.set()
    bp.start()
    logger.info("Back polling started")

    app.exec()

    # Exit
    if front_state.running_event.is_set():
        post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-close-session", {"result": 'abort'}, f"Front2Back: {'abort'} session")
        front_state.clear()
    if front_state.tailscale_connected_event.is_set():
        time.sleep(1)
        res = post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-disconnect", {}, "Front2Back: Disconnect")
        if res:
            front_state.tailscale_disconnect_event.wait()
            front_state.main_screen.append_log("Disconnect succeeded.")
        else:
            front_state.main_screen.append_log("Unable to disconnect properly.")
    front_state.poll_back_event.clear()
    post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/shutdown", {}, "Front2Back: shutdown")


if __name__ == "__main__":
    main()

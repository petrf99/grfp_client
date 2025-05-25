import requests
import time
import threading

from tech_utils.logger import init_logger
logger = init_logger("Front_BCK_Listener")

class SessionState:
    def __init__(self):
        self.abort_event = threading.Event()
        self.finish_event = threading.Event()
        self.connected_event = threading.Event()
        self.external_stop_event = threading.Event()

    def clear(self):
        self.abort_event.clear()
        self.finish_event.clear()
        self.connected_event.clear()

sess_state = SessionState()



from client.front.config import CLIENT_BACK_SERV_PORT, BACK_POLLING_INTERVAL

url = f"http://127.0.0.1:{CLIENT_BACK_SERV_PORT}/get-message"

def back_polling():
    from client.front.logic.input_handlers import state
    global url
    try:
        while True:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                message = res.text
                if message == "abort":
                    logger.info("Abort command received from Back-end")
                    print("Abort command received from Back-end. Stopping the session")
                    sess_state.abort_event.set()
                    sess_state.external_stop_event.set()
                    time.sleep(1)
                    sess_state.clear()
                    state.clear()
                    print("Session stopped.")
                elif message == "finish":
                    logger.info("Finish command received from Back-end")
                    print("Finish command received from Back-end. Stopping the session.")
                    sess_state.finish_event.set()
                    sess_state.external_stop_event.set()
                    time.sleep(1)
                    sess_state.clear()
                    state.clear()
                    print("Session stopped.")
                elif message == "connected":
                    sess_state.connected_event.set()
                    print("Session connected. Press Enter to continue")
                    logger.info("Session connected")
                else:
                    print(message)

            time.sleep(BACK_POLLING_INTERVAL)

    except Exception as e:
        logger.error(f"Unsuccessfull get-message attempt to Back. Exception: {e}. Retrying...")

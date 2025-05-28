from tech_utils.logger import init_logger
logger = init_logger("Back_Main")

from client.back.front_communication.local_server import run_back_server, shutdown_back_server
from client.back.gcs_communication.tcp_communication import run_client_server
from client.back.state import client_state
import time

def main():
    logger.info("Starting Back")
    try:
        run_back_server()
        run_client_server()
        client_state.stop_back_event.wait()
        logger.info("Stopping Back")
        return 0
    except KeyboardInterrupt:
        shutdown_back_server()
        logger.info("Stopping Back")
        return -1

if __name__ == '__main__':
    main()
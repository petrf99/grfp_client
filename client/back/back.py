from tech_utils.logger import init_logger

from client.back.front_communication.local_server import run_back_server
from tech_utils.flask_server_utils import shutdown_server
from client.back.gcs_communication.tcp_communication import run_client_server
from client.back.state import client_state
from client.back.config import BACK_SERV_PORT
import time

logger = init_logger(name="Main", component="back")

def main():
    """
    Entry point for the Client Backend process.
    
    Responsibilities:
    - Start local server for communication with frontend
    - Start TCP server to communicate with GCS
    - Wait for the event signaling backend shutdown
    """
    logger.info("Starting Client Backend")

    try:
        run_back_server()
        run_client_server()

        # Wait until the event signals shutdown (e.g., from front or session end)
        client_state.stop_back_event.wait()

        logger.info("Client Backend stopping")
        return 0

    except KeyboardInterrupt:
        logger.warning("Interrupted by user — shutting down")
        shutdown_server("127.0.0.1", BACK_SERV_PORT, None, logger=logger)
        logger.info("Client Backend stopped via KeyboardInterrupt")
        return -1


if __name__ == '__main__':
    main()

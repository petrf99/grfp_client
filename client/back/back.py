from tech_utils.logger import init_logger
logger = init_logger("Back_Main")

from client.back.front_communication.local_server import run_back_server, running, shutdown_back_server

def main():
    try:
        run_back_server()
        while running.is_set():
            pass
        return 0
    except KeyboardInterrupt:
        shutdown_back_server()
        return -1

if __name__ == '__main__':
    main()
from client.front.state import step_handlers, front_state

from tech_utils.logger import init_logger
logger = init_logger("Front_Main")

def main():
    logger.info("Starting Front")
    current_step = "greeting"
    history = []

    while current_step:
        handler = step_handlers[current_step]
        current_step = handler(front_state)

    logger.info("Stopping front")
    import sys
    sys.exit(0)


if __name__ == "__main__":
    main()

    
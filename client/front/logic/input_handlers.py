import threading
import time
import re

from client.front.logic.back_listener import back_polling
from client.front.config import HELP_FILE_PATH, BACK_SERV_PORT
from tech_utils.cli_input import input_with_back
from tech_utils.safe_post_req import post_request
from client.front.gui.gui_loop import gui_loop
from tech_utils.logger import init_logger

logger = init_logger("Front_Handlers")
BASE_URL = f"http://127.0.0.1:{BACK_SERV_PORT}"

uuid4_regex = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)

# === Step: Greeting and initial setup ===
def step_greeting(state):
    logger.info("Greeting step")
    print("\nWelcome to the Remote Flights Platform Client.")

    # Start background polling thread for back-end updates
    bp = threading.Thread(target=back_polling, daemon=True)
    state.poll_back_event.set()
    bp.start()

    try:
        while True:
            cmd = input("Type 'start' to begin: ").strip().lower()
            if cmd == "start":
                return "free_input"
            elif cmd == "help":
                try:
                    with open(HELP_FILE_PATH, "r") as f:
                        print(f.read())
                except:
                    print("Error")
            elif cmd in ['exit', 'leave']:
                return "done"
            else:
                print("Unknown command. Please type 'start'.")
    except KeyboardInterrupt:
        return "done"

# === Step: Free input mode ===
def step_free_input(state):
    logger.info("Free input step")
    print("\nFree input: type 'connect'/'disconnect' to manage Tailscale, or wait for GCS to offer a session.")

    try:
        while True:
            cmd = input()
            if not cmd:
                continue

            logger.info(f"{cmd} command received")

            if cmd == "help":
                try:
                    with open(HELP_FILE_PATH, "r") as f:
                        print(f.read())
                except:
                    print("\nError reading help file.")
                continue

            elif cmd == "status":
                print(state.status())
                continue

            elif cmd == "disconnect":
                if state.tailscale_connected_event.is_set():
                    res = post_request(f"{BASE_URL}/front-disconnect", {}, "Front2Back: Disconnect")
                    if res:
                        print("\nWaiting for Tailscale to disconnect...")
                        state.tailscale_disconnect_event.wait()
                    else:
                        print("\nFailed to disconnect")
                else:
                    print("You are not connected.")

                state.clear()
                continue

            elif cmd == "connect":
                return "mission_id_input"

            elif cmd in ["exit", "leave"]:
                return "done"

            elif cmd == "launch":
                res = post_request(f"{BASE_URL}/front-launch-session", {}, "Front2Back: Launch session")
                if res:
                    result = "finish" if gui_loop(state) else "abort"
                    post_request(f"{BASE_URL}/front-close-session", {"result": result}, f"Front2Back: {result} session")
                    return "done"
                else:
                    print(f"\nCannot execute '{cmd}'")
                continue

            elif cmd in ["finish", "abort"]:
                result = cmd
                (state.finish_event if result == "finish" else state.abort_event).set()

                res = post_request(f"{BASE_URL}/front-close-session", {"result": result}, f"Front2Back: {result} session")
                state.clear()

                if res:
                    print(f"\nSession {cmd} executed successfully.")
                else:
                    print(f"\nFailed to {cmd} session.")

                state.session_id = None
                return "free_input"

            else:
                print("Unknown command")
                continue

    except KeyboardInterrupt:
        logger.warning("Free input state interrupted by user")
        return "done"

# === Step: Mission ID input (UUID) ===
def step_mission_id_input(state):
    print("\nEnter your mission ID (UUID) or type 'cancel':")
    cmd = input_with_back()

    if not cmd or cmd.lower() == "cancel":
        return "free_input"

    if uuid4_regex.match(cmd):
        res = post_request(f"{BASE_URL}/front-connect", {"mission_id": cmd}, f"Front2Back: Connect with mission {cmd}")
        print("Waiting for Tailscale connection...")
        state.tailscale_connected_event.wait()
        return "free_input"
    else:
        print("\nInvalid input. Expected UUID format.")
        return "mission_id_input"

# === Step: Exit and shutdown ===
def step_done(state):
    if state.tailscale_connected_event.is_set():
        time.sleep(1)
        res = post_request(f"{BASE_URL}/front-disconnect", {}, "Front2Back: Disconnect")
        if res:
            state.tailscale_disconnect_event.wait()
            print("Disconnect succeeded.")
        else:
            print("Unable to disconnect properly.")
    state.poll_back_event.clear()
    post_request(f"{BASE_URL}/shutdown", {}, "Front2Back: shutdown")

    print("\nExiting RFP Client CLI. Goodbye!")
    return None

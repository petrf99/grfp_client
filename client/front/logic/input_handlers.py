from client.front.logic.back_listener import back_polling
import threading
import time

import re
uuid4_regex = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE)

from client.front.config import HELP_FILE_PATH, BACK_SERV_PORT
BASE_URL = f"http://127.0.0.1:{BACK_SERV_PORT}"

from tech_utils.cli_input import input_with_back
from tech_utils.safe_post_req import post_request
from client.front.gui.gui_loop import gui_loop

from tech_utils.logger import init_logger
logger = init_logger("Front_Handlers")

# Free input mode
def step_free_input(state):
    logger.info("Free input step")
    print("\nFree input: type 'connect'/'disconnect' to connect on Tailnet or just wait till your GCS offers you a session")
    try:
        while True:
            cmd = input()
            if cmd is None:
                continue
            
            logger.info(f"{cmd} command received")

            if cmd == "help":
                try:
                    with open(HELP_FILE_PATH, "r") as f:
                        print(f.read())
                except:
                    print("\nError")
                    continue

            elif cmd == 'disconnect':
                if state.tailscale_connected_event.is_set():
                    res = post_request(url = f"{BASE_URL}/front-disconnect", payload={}, description="Front2Back: Disconnect")
                    if res:
                        print("\nPlease wait until Tailscale disconnects")
                        while state.tailscale_connected_event.is_set():
                            time.sleep(1)
                            pass
                    else:
                        print("\nUnable to disconnect properly")

                else:
                    print("You aren't connected")
                continue
            
            elif cmd == 'connect':
                return "mission_id_input"

            elif cmd in ['exit', 'leave']:
                return "done"
            
            elif cmd == "launch":
                res = post_request(url = f"{BASE_URL}/front-launch-session", payload={},
                                    description=f"Front2Back: Launch session")
                
                if res:
                    result = 'finish' if gui_loop(state) else 'abort'
                    post_request(url = f"{BASE_URL}/front-close-session", payload={"result": result},
                                    description=f"Front2Back: {result} session")
                    return "done"
                else:
                    print(f"\nCan't execute {cmd}")
                continue
            
            elif cmd == "finish" or cmd == "abort":
                result = cmd.split()[0]
                if cmd == 'finish':
                    state.finish_event.set()
                else:
                    state.abort_event.set()

                res = post_request(url = f"{BASE_URL}/front-close-session", payload={"result": result},
                                    description=f"Front2Back: {result} session")
                
                state.clear()

                if res:
                    print(f"\n{cmd} executed successfully")
                else:
                    print(f"\nCan't execute {cmd}")
                return "free_input"

            else:
                print("Unknown command")
                continue
                
    except KeyboardInterrupt:
        logger.warning("Free input state interrupted by keyboard")
        return "done"
    

# Step 1
def step_greeting(state):
    logger.info("Greeting step")
    print("\nWelcome to the Remote Flights Platform Client.")

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
                    continue
            elif cmd in ['exit', 'leave']:
                return "done"

            print("Unknown command. Please type 'start'.")
    except KeyboardInterrupt:
        return "done"


# Done
def step_done(state):
    state.poll_back_event.clear()
    if state.tailscale_connected_event.is_set():
        time.sleep(1)
        res = post_request(url = f"{BASE_URL}/front-disconnect", payload={}, description="Front2Back: Disconnect")
        if res:
            print("Disconnect succeeded.")
        else:
            print("Unable to disconnect properly")
    time.sleep(1)
    post_request(url = f"{BASE_URL}/shutdown", 
                                   payload={},
                                 description=f"Front2Back: shutdown")
    print("\nExiting RFP Client CLI. Goodbye!")
    return None


def step_mission_id_input(state):
    print("\nPlease enter your mission identifier (UUID) (or type 'cancel')")
    cmd = input_with_back()

    if cmd is None or cmd == 'cancel':
        return "free_input"
    
    if bool(uuid4_regex.match(cmd)):
        res = post_request(url=f"{BASE_URL}/front-connect",
                           payload={"mission_id":cmd}, 
                           description=f"Front2Back: Connect with mission {cmd}")
        print("Please wait until Tailscale connects")
        state.tailscale_connected_event.wait()
        return "free_input"
    
    else:
        print("\nUnknown command")
        return "mission_id_input"


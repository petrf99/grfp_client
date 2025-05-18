from threading import Thread

from tech_utils.logger import init_logger
logger = init_logger("RCClient_Main")


from client.config import FREQUENCY, RC_CHANNELS_DEFAULTS

from client.session_manager.token_auth import get_valid_token

from client.gcs_communication.tailscale_connect import start_tailscale, wait_for_tailscale_ips
from client.gcs_communication.send_message_to_gcs import send_start_message_to_gcs, run_client_server

from client.gcs_communication.udp_rc_input_sender import send_rc_frame
from client.gcs_communication.udp_drone_data_receiver import telemetry_receiver

from client.inputs import select_controller, get_rc_input

from client.gui.pygame import pygame_init, pygame_event_get, pygame_quit, pygame_QUIT

from client.session_manager.basic_commands import ready, abort, stop, leave


def run_main_loop(session_id: str, gcs_ip: str, client_ip: str, controller: str):

    # === Initialize pygame ===
    screen, clock = pygame_init()

    # Get the controller
    rc_input = get_rc_input(controller)


    # === Создание UDP-сокета ===
    from client.gcs_communication.udp_rc_input_sender import get_socket
    sock = get_socket()

    # === Telemetry receiver === 
    recv_thread = Thread(target=telemetry_receiver, args=(sock,), daemon=True)
    recv_thread.start()

    # === Главный цикл ===
    rc_state = RC_CHANNELS_DEFAULTS.copy()

    logger.info(f"RC Session ID: {session_id}\n")

    running = True
    while running:
        clock.tick(FREQUENCY)
        for event in pygame_event_get():
            if event.type == pygame_QUIT:
                running = False
            rc_state = rc_input.process_event(event, rc_state)

        rc_state = rc_input.read_frame(rc_state)

        send_rc_frame(sock, session_id, rc_state, controller, gcs_ip)


    # отправить финальный neutral frame (disarm дрона при выходе)
    neutral = RC_CHANNELS_DEFAULTS.copy()
    neutral["ch5"] = 1000
    neutral["ch6"] = 1000
    send_rc_frame(sock, session_id, neutral, controller, gcs_ip)

    pygame_quit()

    return abort(gcs_ip, session_id, sock, good=True)


def main():
    auth_token, session_id = get_valid_token()
    if not session_id:
        return leave()

    if not start_tailscale(auth_token):
        return leave()

    Thread(target=run_client_server, daemon=True).start()
    
    ips = wait_for_tailscale_ips(session_id)
    if not ips:
        return stop()
    else:
        gcs_ip, client_ip = ips[0], ips[1]

    if send_start_message_to_gcs(gcs_ip, session_id):
        controller = select_controller()
        if not controller:
            return abort(gcs_ip, session_id)
        
        is_ready = ready()
        if not is_ready:
            return abort(gcs_ip, session_id)
        else:
            run_main_loop(session_id, gcs_ip, client_ip, controller)
    else:
        print("❌ Aborting. Could not reach GCS.")
        logger.error(f"{session_id} Aborting. Could not reach GCS.")
        return stop()


if __name__ == "__main__":
    main()


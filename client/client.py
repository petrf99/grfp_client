from threading import Thread

from tech_utils.logger import init_logger
logger = init_logger("Client_Main")


from client.config import FREQUENCY, RC_CHANNELS_DEFAULTS

from client.gcs_communication.tailscale_connect import start_tailscale, wait_for_tailscale_ips
from client.gcs_communication.tcp_communication import send_start_message_to_gcs, run_client_server, keep_connection

from client.gcs_communication.udp_rc_input_sender import send_rc_frame
from client.gcs_communication.udp_drone_data_receiver import telemetry_receiver

from client.inputs import get_rc_input

from client.gui.pygame import pygame_init, pygame_event_get, pygame_quit, pygame_QUIT

from client.session_manager.basic_commands import disconnect, close, leave
from client.session_manager.user_input import ready, select_controller, enter_token

from client.session_manager.events import finish_event, abort_event


def streaming_loop(session_id, gcs_ip, clock, rc_input, controller, sock):
    rc_state = RC_CHANNELS_DEFAULTS.copy()
    try:
        while not finish_event.is_set() and not abort_event.is_set():
            clock.tick(FREQUENCY)
            for event in pygame_event_get():
                if event.type == pygame_QUIT:
                    finish_event.set()
                rc_state = rc_input.process_event(event, rc_state)

            rc_state = rc_input.read_frame(rc_state)

            send_rc_frame(sock, session_id, rc_state, controller, gcs_ip)
        pygame_quit()
    except KeyboardInterrupt:
        logger.warning("User interrupted during main_control_loop(). Aborting session.")
        abort_event.set()
        return False
    
    return finish_event.is_set()


def run_main_loop(session_id: str, gcs_ip: str, client_ip: str, controller: str):
    # === Pinging the GCS ===
    keep_conn_thread = Thread(target = keep_connection, args = (client_ip, session_id), daemon=True)
    keep_conn_thread.start()

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

    logger.info(f"Session ID: {session_id}\n")

    good_finish = streaming_loop(session_id, gcs_ip, clock, rc_input, controller, sock)

    
    print("Session complete.")

    return close(gcs_ip, session_id, sock, finish_flg=good_finish)


def main():
    logger.info("Start the program")
    result = enter_token()
    if isinstance(result, tuple) and len(result) == 2:
        auth_token, session_id = result
    else:
        return leave()


    if not start_tailscale(session_id, auth_token):
        return leave()

    Thread(target=run_client_server, daemon=True).start()
    
    ips = wait_for_tailscale_ips(session_id, auth_token)
    if not ips:
        return disconnect()
    else:
        gcs_ip, client_ip = ips[0], ips[1]

    if send_start_message_to_gcs(gcs_ip, session_id):
        controller = select_controller()
        if not controller:
            return close(gcs_ip, session_id)
        
        is_ready = ready()
        if not is_ready:
            return close(gcs_ip, session_id)
        else:
            return run_main_loop(session_id, gcs_ip, client_ip, controller)
    else:
        logger.error(f"{session_id} Aborting. Could not reach GCS.")
        return disconnect()


if __name__ == "__main__":
    main()


import numpy as np
import pygame
import time
import threading
import cv2

from tech_utils.logger import init_logger
logger = init_logger("Front_GUI")

from client.front.config import FREQUENCY, RC_CHANNELS_DEFAULTS, TELEMETRY_GUI_DRAW_FIELDS, NO_FRAME_MAX, CLIENT_TLMT_RECV_PORT

from client.front.logic.data_listeners import get_video_cap, get_telemetry, telemetry_data
from client.front.gui.pygame import pygame_init, pygame_event_get, pygame_quit, pygame_QUIT
from client.front.logic.back_sender import send_rc_frame
from client.front.logic.back_listener import sess_state


def gui_loop(session_id, rc_input, controller):
    global telemetry_data

    try:
        # === Initialize pygame ===
        screen, font, clock = pygame_init()

        rc_state = RC_CHANNELS_DEFAULTS.copy()
        
        telemetry_values = {'no data': ''}

        cap = get_video_cap(100)

        from tech_utils.udp import get_socket
        sock = get_socket()
        tlmt_sock = get_socket("0.0.0.0", CLIENT_TLMT_RECV_PORT, bind=True)

        threading.Thread(target=get_telemetry, args=(tlmt_sock,), daemon=True).start()
        

        while not sess_state.finish_event.is_set() and not sess_state.abort_event.is_set():
            clock.tick(FREQUENCY)

            # 🎮 Обработка событий
            for event in pygame_event_get():
                if event.type == pygame_QUIT:
                    sess_state.finish_event.set()
                    break
                rc_state = rc_input.process_event(event, rc_state)

            if sess_state.finish_event.is_set():
                break

            rc_state = rc_input.read_frame(rc_state)
            send_rc_frame(sock, session_id, rc_state, controller)

            # 🎥 Получение кадра из видео
            ret, frame = cap.read()
            if ret:
                no_frame_counter = 0
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.flip(frame, axis=0)
                frame = np.rot90(frame, k=-1)  # Повернуть на 90° по часовой
                surface = pygame.surfarray.make_surface(frame)
                screen.blit(surface, (0, 0))
            else:
                no_frame_counter += 1
                if no_frame_counter >= NO_FRAME_MAX:
                    logger.warning("🔁 Reinitializing video stream...")
                    cap.release()
                    cap = get_video_cap(30)
                    no_frame_counter = 0
                else:
                    logger.warning("⚠️ Frame not received — waiting...")
                    time.sleep(0.1)
                continue



            # 📡 HUD телеметрии
            hud_lines = []
            telemetry_snapshot = telemetry_data.copy()
            if isinstance(telemetry_snapshot, dict):
                telemetry_values = telemetry_snapshot.copy()
            else:
                logger.warning("⚠️ telemetry_data is not a valid dict: %s", telemetry_snapshot)
                telemetry_values = {'no data': ''} 


            for k, v in telemetry_values.items():
                if k in TELEMETRY_GUI_DRAW_FIELDS + ["round_trip_time_ms"]:
                    if isinstance(v, dict):
                        hud_lines.append(f"{k}:")
                        for k_, v_ in v.items():
                            #if k_ == 'init_timestamp':
                            #    full_ping = time.time() - v_
                            #    hud_lines.append(f"Apprx ping: {round(full_ping * 100)*10} ms")
                            #else:
                            hud_lines.append(f" {k_}: {v_}")
                    else:
                        hud_lines.append(f"{k}: {v}")

            hud_surface = pygame.Surface((250, max(len(hud_lines), 20) * 20), pygame.SRCALPHA)  # прозрачная подложка
            hud_surface.fill((0, 0, 0, 128))  # чёрный с альфой

            # текст поверх
            for i, line in enumerate(hud_lines):
                text = font.render(line, True, (255, 255, 255))
                hud_surface.blit(text, (10, i * 20))

            # теперь наложим HUD на экран
            screen.blit(hud_surface, (0, 0))


            pygame.display.flip()

    except KeyboardInterrupt:
        logger.warning("User interrupted during gui_loop(). Aborting session.")
        sess_state.abort_event.set()
        return False
    except Exception as e:
        logger.error(f"{session_id} GUI Loop Error: {e}")
        sess_state.abort_event.set()
        return False

    sock.close()
    tlmt_sock.close()

    cap.release()

    pygame_quit()

    return sess_state.finish_event.is_set()

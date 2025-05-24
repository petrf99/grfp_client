import numpy as np
import pygame
import time
import cv2

from tech_utils.logger import init_logger
logger = init_logger("Front_GUI")

from client.config import FREQUENCY, RC_CHANNELS_DEFAULTS, TELEMETRY_GUI_DRAW_FIELDS

from client.front.gui.utils import get_video_cap, get_telemetry
from client.front.gui.pygame import pygame_init, pygame_event_get, pygame_quit, pygame_QUIT
from client.front.logic.back_interaction import send_rc_frame
from client.front.logic.back_listener import abort_event, finish_event


def gui_loop(session_id, rc_input, controller):


    try:
        # === Initialize pygame ===
        screen, font, clock = pygame_init()

        rc_state = RC_CHANNELS_DEFAULTS.copy()

        cap = get_video_cap(100)
        

        while not finish_event.is_set() and not abort_event.is_set():
            clock.tick(FREQUENCY)

            # 🎮 Обработка событий
            for event in pygame_event_get():
                if event.type == pygame_QUIT:
                    finish_event.set()
                rc_state = rc_input.process_event(event, rc_state)

            rc_state = rc_input.read_frame(rc_state)
            send_rc_frame(session_id, rc_state, controller)

            # 🎥 Получение кадра из видео
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.flip(frame, axis=0)
                frame = np.rot90(frame, k=-1)  # Повернуть на 90° по часовой
                surface = pygame.surfarray.make_surface(frame)
                screen.blit(surface, (0, 0))
            else:
                text = font.render("📡 Waiting for video...", True, (255, 0, 0))
                screen.blit(text, (50, 50))
                logger.warning("⚠️ Failed to read video frame — stream lost?")
                time.sleep(0.1)
                continue


            # 📡 HUD телеметрии
            telemetry_snapshot = get_telemetry()
            if not telemetry_snapshot:
                logger.warning("⚠️ telemetry_data is empty!")
            hud_lines = []
            with open("logs/RC_round_trip_pings.log", "a") as rcrt_log:
                for k, v in telemetry_snapshot.items():
                    if k in TELEMETRY_GUI_DRAW_FIELDS:
                        if isinstance(v, dict):
                            hud_lines.append(f"{k}:")
                            for k_, v_ in v.items():
                                if k_ == 'init_timestamp':
                                    full_ping = time.time() - v_
                                    rcrt_log.write(str(round(full_ping * 100/2)*10) + '\n')
                                    hud_lines.append(f"Apprx ping: {round(full_ping * 100/2)*10} ms")
                                else:
                                    hud_lines.append(f" {k_}: {v_}")
                        else:
                            hud_lines.append(f"{k}: {v}")
            hud_surface = pygame.Surface((250, len(hud_lines) * 20), pygame.SRCALPHA)  # прозрачная подложка
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
        abort_event.set()
        return False
    except Exception as e:
        logger.error(f"{session_id} GUI Loop Error: {e}")
        abort_event.set()
        return False

    cap.release()
    pygame_quit()

    return finish_event.is_set()

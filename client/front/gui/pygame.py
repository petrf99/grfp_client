import pygame

from tech_utils.logger import init_logger
logger = init_logger("Front_GUI")

from client.config import *

pygame_QUIT = pygame.QUIT

def pygame_init(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="RC Controller"):
    try:
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((width, height))
    except pygame.error as e:
        logger.error(f"[ERROR] Pygame init failed: {e}", exc_info=True)
        raise

    # 🖥️ Инициализация экрана
    font = pygame.font.Font(None, 24)  # безопасный способ
    if font is None:
        logger.error("Font failed to load!")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    return screen, font, clock

def pygame_event_get():
    return pygame.event.get()

def pygame_quit():
    pygame.quit()

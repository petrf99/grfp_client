import pygame

from tech_utils.logger import init_logger
logger = init_logger("Front_GUI")

from client.front.config import SCREEN_HEIGHT, SCREEN_WIDTH

pygame_QUIT = pygame.QUIT

def pygame_init(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="RC Controller"):
    try:
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((width, height))
    except pygame.error as e:
        logger.error(f"[ERROR] Pygame init failed: {e}", exc_info=True)
        raise

    # 🖥️ Screen initialization
    font = pygame.font.Font(None, 24)  
    if font is None:
        logger.error("Font failed to load!")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    return screen, font, clock

def pygame_event_get():
    return pygame.event.get()

def pygame_quit():
    try:
        pygame.display.quit()
        pygame.quit()
    except Exception as e:
        print(f"Error during pygame quit: {e}")

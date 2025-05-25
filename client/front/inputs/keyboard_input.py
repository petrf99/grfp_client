import pygame
from client.front.config import STEP_ANALOG, LIMIT_MIN, LIMIT_MAX
from client.back.inputs.base_input import BaseRCInput

class KeyboardInput(BaseRCInput):
    def __init__(self):
        super().__init__()
        self.toggle_flags = {"armed": False, "aux": False}

    def process_event(self, event, rc_state):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.toggle_flags["armed"] = not self.toggle_flags["armed"]
            rc_state["ch5"] = 1900 if self.toggle_flags["armed"] else 1000

        if event.type == pygame.KEYDOWN and (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT):
            self.toggle_flags["aux"] = not self.toggle_flags["aux"]
            rc_state["ch6"] = 1900 if self.toggle_flags["aux"] else 1000

        return rc_state

    def read_frame(self, rc_state):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            rc_state["ch3"] = min(rc_state["ch3"] + STEP_ANALOG, LIMIT_MAX)
        if keys[pygame.K_s]:
            rc_state["ch3"] = max(rc_state["ch3"] - STEP_ANALOG, LIMIT_MIN)
        if keys[pygame.K_a]:
            rc_state["ch4"] = max(rc_state["ch4"] - STEP_ANALOG, LIMIT_MIN)
        if keys[pygame.K_d]:
            rc_state["ch4"] = min(rc_state["ch4"] + STEP_ANALOG, LIMIT_MAX)

        if keys[pygame.K_LEFT]:
            rc_state["ch1"] = max(rc_state["ch1"] - STEP_ANALOG, LIMIT_MIN)
        if keys[pygame.K_RIGHT]:
            rc_state["ch1"] = min(rc_state["ch1"] + STEP_ANALOG, LIMIT_MAX)
        if keys[pygame.K_UP]:
            rc_state["ch2"] = min(rc_state["ch2"] + STEP_ANALOG, LIMIT_MAX)
        if keys[pygame.K_DOWN]:
            rc_state["ch2"] = max(rc_state["ch2"] - STEP_ANALOG, LIMIT_MIN)

        return rc_state

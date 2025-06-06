from PySide6.QtCore import Qt, QPoint
from client.front.config import STEP_ANALOG, LIMIT_MIN, LIMIT_MAX
from client.front.inputs.base_input import BaseRCInput


class MouseKeyboardInputQt(BaseRCInput):
    def __init__(self):
        super().__init__()
        self.toggle_flags = {"armed": False, "aux": False}
        self.pressed_keys = set()
        self.prev_mouse_pos = None
        self.delta_accum = QPoint(0, 0)

    def update_mouse_position(self, pos: QPoint):
        if self.prev_mouse_pos is not None:
            delta = pos - self.prev_mouse_pos
            self.delta_accum += delta
        self.prev_mouse_pos = pos

    def handle_key_press(self, event, rc_state):
        key = event.key()
        self.pressed_keys.add(key)

        if key == Qt.Key_Space:
            self.toggle_flags["armed"] = not self.toggle_flags["armed"]
            rc_state["ch5"] = 1900 if self.toggle_flags["armed"] else 1000

        if key in (Qt.Key_Shift,):
            self.toggle_flags["aux"] = not self.toggle_flags["aux"]
            rc_state["ch6"] = 1900 if self.toggle_flags["aux"] else 1000

        return rc_state

    def handle_key_release(self, event):
        key = event.key()
        self.pressed_keys.discard(key)

    def read_frame(self, rc_state, sensitivity):
        # Клавиши: throttle и roll
        if Qt.Key_W in self.pressed_keys:
            rc_state["ch3"] = min(rc_state["ch3"] + int(sensitivity * STEP_ANALOG), LIMIT_MAX)
        if Qt.Key_S in self.pressed_keys:
            rc_state["ch3"] = max(rc_state["ch3"] - int(sensitivity * STEP_ANALOG), LIMIT_MIN)
        if Qt.Key_A in self.pressed_keys:
            rc_state["ch4"] = max(rc_state["ch4"] - int(sensitivity * STEP_ANALOG), LIMIT_MIN)
        if Qt.Key_D in self.pressed_keys:
            rc_state["ch4"] = min(rc_state["ch4"] + int(sensitivity * STEP_ANALOG), LIMIT_MAX)

        # Mouse: yaw и pitch
        # Мышь: теперь по накопленному delta
        dx = self.delta_accum.x()
        dy = self.delta_accum.y()

        rc_state["ch1"] = self._clamp_channel(rc_state["ch1"] + int(dx * sensitivity))
        rc_state["ch2"] = self._clamp_channel(rc_state["ch2"] - int(dy * sensitivity))  # инверсия Y

        # Обнуляем накопление после применения
        self.delta_accum = QPoint(0, 0)

        return rc_state

    def _clamp_channel(self, value):
        return max(min(value, LIMIT_MAX), LIMIT_MIN)

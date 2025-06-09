from PySide6.QtCore import Qt, QPoint
from client.front.config import STEP_ANALOG, LIMIT_MIN, LIMIT_MAX
from client.front.inputs.base_input import BaseRCInput


class MouseKeyboardInputQt(BaseRCInput):
    def __init__(self, params):
        super().__init__(params)
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

        if key == Qt.Key_Shift:
            self.toggle_flags["aux"] = not self.toggle_flags["aux"]
            rc_state["ch6"] = 1900 if self.toggle_flags["aux"] else 1000

        return rc_state

    def handle_key_release(self, event):
        key = event.key()
        self.pressed_keys.discard(key)

    def read_frame(self, rc_state):
        # Клавиатурные приращения
        delta_throttle = 0
        delta_yaw = 0

        if Qt.Key_W in self.pressed_keys:
            delta_throttle += STEP_ANALOG
        if Qt.Key_S in self.pressed_keys:
            delta_throttle -= STEP_ANALOG
        if Qt.Key_D in self.pressed_keys:
            delta_yaw += STEP_ANALOG
        if Qt.Key_A in self.pressed_keys:
            delta_yaw -= STEP_ANALOG

        rc_state["ch3"] = self._clamp_channel(rc_state["ch3"] + int(delta_throttle * self.sensitivity))
        rc_state["ch4"] = self._clamp_channel(rc_state["ch4"] + int(delta_yaw * self.sensitivity))

        # Мышиные приращения (накопленные)
        dx = self.delta_accum.x()
        dy = self.delta_accum.y()

        # Можно считать dx/dy как аналоговое значение в диапазоне, например, -20..20
        max_input = 30  # чувствительность при большой мыши
        raw_x = max(-max_input, min(max_input, dx))
        raw_y = max(-max_input, min(max_input, dy))

        # Применим кривую чувствительности
        mapped_roll = self.apply_axis_curve(raw_x, in_min=-max_input, in_max=max_input,
                                            out_min=-STEP_ANALOG, out_max=STEP_ANALOG)
        mapped_pitch = self.apply_axis_curve(-raw_y, in_min=-max_input, in_max=max_input,  # инверсия Y
                                             out_min=-STEP_ANALOG, out_max=STEP_ANALOG)

        rc_state["ch1"] = self._clamp_channel(rc_state["ch1"] + mapped_roll)
        rc_state["ch2"] = self._clamp_channel(rc_state["ch2"] + mapped_pitch)

        # Сброс мышиных дельт
        self.delta_accum = QPoint(0, 0)

        return rc_state

    def _clamp_channel(self, value):
        return max(LIMIT_MIN, min(value, LIMIT_MAX))

from PySide6.QtCore import Qt
from client.front.config import STEP_ANALOG, LIMIT_MIN, LIMIT_MAX
from client.front.inputs.base_input import BaseRCInput

class KeyboardInputQt(BaseRCInput):
    def __init__(self, params):
        super().__init__(params)
        self.toggle_flags = {"armed": False, "aux": False}
        self.pressed_keys = set()

    def handle_key_press(self, event, rc_state):
        key = event.key()
        self.pressed_keys.add(key)

        if key == Qt.Key_Space:
            self.toggle_flags["armed"] = not self.toggle_flags["armed"]
            rc_state["ch5"] = 1900 if self.toggle_flags["armed"] else 1000

        if key in (Qt.Key_Shift, Qt.Key_Shift):  # обе шифт-клавиши
            self.toggle_flags["aux"] = not self.toggle_flags["aux"]
            rc_state["ch6"] = 1900 if self.toggle_flags["aux"] else 1000

        return rc_state

    def handle_key_release(self, event):
        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def read_frame(self, rc_state):
        step = STEP_ANALOG  # базовый шаг
        s = self.sensitivity  # чувствительность

        # throttle (W/S)
        if Qt.Key_W in self.pressed_keys:
            rc_state["ch3"] = self._clamp_channel(rc_state["ch3"] + int(step * s))
        if Qt.Key_S in self.pressed_keys:
            rc_state["ch3"] = self._clamp_channel(rc_state["ch3"] - int(step * s))

        # yaw (A/D)
        if Qt.Key_A in self.pressed_keys:
            rc_state["ch4"] = self._clamp_channel(rc_state["ch4"] - int(step * s))
        if Qt.Key_D in self.pressed_keys:
            rc_state["ch4"] = self._clamp_channel(rc_state["ch4"] + int(step * s))

        # roll (← →)
        if Qt.Key_Left in self.pressed_keys:
            rc_state["ch1"] = self._clamp_channel(rc_state["ch1"] - int(step * s))
        if Qt.Key_Right in self.pressed_keys:
            rc_state["ch1"] = self._clamp_channel(rc_state["ch1"] + int(step * s))

        # pitch (↑ ↓)
        if Qt.Key_Up in self.pressed_keys:
            rc_state["ch2"] = self._clamp_channel(rc_state["ch2"] + int(step * s))
        if Qt.Key_Down in self.pressed_keys:
            rc_state["ch2"] = self._clamp_channel(rc_state["ch2"] - int(step * s))

        return rc_state

    def _clamp_channel(self, value):
        return max(LIMIT_MIN, min(value, LIMIT_MAX))
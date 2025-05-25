class BaseRCInput:
    def __init__(self):
        self.toggle_flags = {}

    def process_event(self, event, rc_state):
        """Обрабатывает дискретные события (нажатия клавиш/кнопок)"""
        return rc_state

    def read_frame(self, rc_state):
        """Обрабатывает удержание (например, стики, клавиши)"""
        return rc_state

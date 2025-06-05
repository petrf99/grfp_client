class BaseRCInput:
    def __init__(self):
        self.toggle_flags = set()  # или dict, если нужны значения

    def handle_key_press(self, event, rc_state):
        """Обрабатывает однократное нажатие клавиши (например, toggle)"""
        return rc_state

    def handle_key_release(self, event):
        """Обрабатывает отпускание клавиши"""
        pass

    def read_frame(self, rc_state):
        """Обрабатывает непрерывное удержание (например, движение)"""
        return rc_state

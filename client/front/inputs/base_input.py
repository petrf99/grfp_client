class BaseRCInput:
    def __init__(self, params):
        self.toggle_flags = set()
        self.deadzone = params.get("deadzone", 0.0)
        self.expo = params.get("expo", 0.0)
        self.sensitivity = params.get("sensitivity", 1.0)

    def apply_axis_curve(self, value, in_min=0, in_max=255, out_min=1000, out_max=2000):
        """
        Применяет deadzone, expo и sensitivity к осевому значению.
        """
        center = (in_max + in_min) // 2
        # 1. Применим deadzone
        dz = (in_max - in_min) * self.deadzone
        if abs(value - center) < dz:
            value = center

        # 2. Нормализуем в диапазон -1 ... 1
        x = (value - center) / (in_max - in_min) * 2

        # 3. Применим expo (мягкое скругление около центра)
        x_exp = x * (1 - self.expo) + (x ** 3) * self.expo

        # 4. Применим чувствительность
        x_final = x_exp * self.sensitivity
        x_final = max(-1.0, min(1.0, x_final))  # защита от выхода за границы

        # 5. Обратно в диапазон RC
        rc_value = int((x_final + 1) / 2 * (out_max - out_min) + out_min)
        return rc_value


    def handle_key_press(self, event, rc_state):
        """Обрабатывает однократное нажатие клавиши (например, toggle)"""
        return rc_state

    def handle_key_release(self, event):
        """Обрабатывает отпускание клавиши"""
        pass

    def read_frame(self, rc_state, sensitivity=1):
        """Обрабатывает непрерывное удержание (например, движение)"""
        return rc_state

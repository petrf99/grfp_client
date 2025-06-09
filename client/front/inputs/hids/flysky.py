from client.front.inputs.hids.generic_class import HIDControllerBase

class FlySkyUSBAdapter(HIDControllerBase):
    def __init__(self, controller_name):
        super().__init__(controller_name)

        # Диапазоны значений осей в репорте
        self.axis_range = {
            "roll": (0, 255),     # ch1
            "pitch": (0, 255),    # ch2
            "throttle": (0, 255), # ch3
            "yaw": (0, 255),      # ch4
        }

    def parse_report(self, data):
        return {
            "ch1": self.apply_axis_curve(data[0], *self.axis_range["roll"]),
            "ch2": self.apply_axis_curve(data[1], *self.axis_range["pitch"]),
            "ch3": self.apply_axis_curve(data[2], *self.axis_range["throttle"]),
            "ch4": self.apply_axis_curve(data[3], *self.axis_range["yaw"]),
            "ch5": 2000 if data[4] & 0b01 else 1000,  # arm
            "ch6": 2000 if data[4] & 0b10 else 1000,  # aux
            **{f"ch{i}": 1000 for i in range(7, 17)}
        }

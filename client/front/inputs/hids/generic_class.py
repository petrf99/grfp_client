import hid
from client.front.inputs.base_input import BaseRCInput

class HIDControllerBase(BaseRCInput):
    def __init__(self, controller, params):
        super().__init__(params)
        self.name = controller
        self.device = None

    def open(self):
        from client.front.inputs import DeviceManager
        if self.device is None:
            self.device = DeviceManager.select_device_by_name(self.name)

    def close(self):
        if self.device:
            self.device.close()
            self.device = None

    def read_raw(self):
        if self.device:
            return self.device.read(64, timeout_ms=100)
        return []
    
    def parse_report(self, data):
        raise NotImplementedError("You must implement parse_report in subclass")

    def read_frame(self, rc_state):
        """Read HID-state and update rc_state"""
        data = self.read_raw()
        if not data:
            return rc_state

        rc = self.parse_report(data)
        rc_state.update(rc)
        return rc_state

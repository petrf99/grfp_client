from client.front.inputs.keyboard_input import KeyboardInputQt
from client.front.inputs.mouse_keyboard_input import MouseKeyboardInputQt
from client.front.inputs.hids.generic_class import HIDControllerBase

from client.front.config import DEFAULT_CONTROLLER
from tech_utils.hid_manager import HidDevices

DeviceManager = HidDevices()

hid_class_matches = {} # (vendor_id, product_id) -> HID Input Class

def get_rc_input(controller=DEFAULT_CONTROLLER, params = {}):
    if controller == "keyboard":
        return KeyboardInputQt(params)
    elif controller == "mouse_keyboard":
        return MouseKeyboardInputQt(params)
    elif controller in hid_class_matches:
        vid_pid = DeviceManager.get_id_by_name(controller)
        if vid_pid is None:
            raise ValueError(f"Unknown input type: {controller}")
        adapter_cls = hid_class_matches.get(vid_pid, HIDControllerBase)
        return adapter_cls(controller, params)
    else:
        raise ValueError(f"Unknown input type: {controller}")

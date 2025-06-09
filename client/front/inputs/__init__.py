from client.front.inputs.keyboard_input import KeyboardInputQt
from client.front.inputs.drone_rc_controller_input import DroneRCControllerInput
from client.front.inputs.gamepad_input import GamepadInput
from client.front.inputs.mouse_keyboard_input import MouseKeyboardInputQt

from client.front.config import DEFAULT_CONTROLLER

def get_rc_input(input_type=DEFAULT_CONTROLLER):
    if input_type == "keyboard":
        return KeyboardInputQt()
    elif input_type == "mouse_keyboard":
        return MouseKeyboardInputQt()
    elif input_type == "gamepad":
        return GamepadInput()
    elif input_type == "rc_controller":
        return DroneRCControllerInput()
    else:
        raise ValueError(f"Unknown input type: {input_type}")

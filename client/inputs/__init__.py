from client.inputs.keyboard_input import KeyboardInput

def get_rc_input(input_type="keyboard"):
    if input_type == "keyboard":
        return KeyboardInput()
    # elif input_type == "gamepad":
    #     return GamepadInput()
    # elif input_type == "radio":
    #     return DroneRadioInput()
    else:
        raise ValueError(f"Unknown input type: {input_type}")

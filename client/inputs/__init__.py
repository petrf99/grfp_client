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

from client.config import CONTROLLERS_LIST

def select_controller():
    print("Please enter the type of your controller:\n1 - keyboard\n2 - mouse+keyboard\n3 - gamepad\n4 - drone remote controller\n\nIf you want to terminate the process type 'abort'")

    while True:
        try:
            inp = input()
            if inp == 'abort':
                return False
            controller_type = int(inp)
            if controller_type >= 1 and controller_type <= len(CONTROLLERS_LIST):
                controller = CONTROLLERS_LIST[controller_type]
                return controller
            else:
                print(f"Please enter a number 1-{len(CONTROLLERS_LIST)}:")
        except:
            print(f"Please enter a number 1-{len(CONTROLLERS_LIST)}:")
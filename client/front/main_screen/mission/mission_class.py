from PySide6.QtWidgets import QWidget
from client.front.main_screen.mission.ui_mission_widget import Ui_MissionWidget
from tech_utils.safe_post_req import post_request
from client.front.config import BACK_SERV_PORT
from client.front.state import front_state

button_pressed_flg = False # Global to forbid different connection attempts simultaneously

class MissionWidget(QWidget):
    def __init__(self, mission_data):
        super().__init__()
        self.ui = Ui_MissionWidget()
        self.ui.setupUi(self)

        self.mission_id = mission_data['mission_id']

        # Fill data from mission_data
        self.ui.labelDroneType.setText(f"Drone: {mission_data['drone_type']}")
        self.ui.labelLocation.setText(f"Location: {mission_data['location']}")
        self.ui.labelMissionGroup.setText(f"Group: {mission_data['mission_group']}")
        self.ui.labelStatus.setText(f"Status: {mission_data['status']}")
        self.ui.labelTimeWindow.setText(f"Time Window: {mission_data['time_window']}")
        self.ui.labelMissionId.setText(f"ID: {mission_data['mission_id']}")

        # Bind button
        self.ui.pushButtonConnect.clicked.connect(self.toggle_connection)

    def toggle_connection(self):
        # Connect/disconnect to Tailnet
        global button_pressed_flg
        if not front_state.tailscale_connected_event.is_set() and not button_pressed_flg and self.ui.pushButtonConnect.text() == "Connect":
            res = post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-connect", {"mission_id": self.mission_id}, f"Front2Back: Connect with mission {self.mission_id}")
            if res:
                front_state.main_screen.append_log("You are being connected to Tailnet. Please wait...")
                front_state.active_mission = self
                button_pressed_flg = True
            else:
                front_state.main_screen.append_log("Couldn't connect to Tailnet. Please contact admin.")
        elif not button_pressed_flg and self.ui.pushButtonConnect.text() == "Disconnect":
            res = post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-disconnect", {}, "Front2Back: Disconnect")
            if res:
                front_state.main_screen.append_log("Waiting for Tailscale to disconnect...")
                button_pressed_flg = True
            else:
                front_state.main_screen.append_log("Failed to disconnect")
        else:
            front_state.main_screen.append_log("Your previous request is being handled.")

    def toggle_button_text(self):
        global button_pressed_flg
        if front_state.tailscale_connected_event.is_set():
            self.ui.pushButtonConnect.setText("Disconnect")
        elif front_state.tailscale_disconnect_event.is_set():
                    self.ui.pushButtonConnect.setText("Connect")
        button_pressed_flg = False
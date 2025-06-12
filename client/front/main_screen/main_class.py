from PySide6.QtWidgets import QWidget, QStackedWidget, QHBoxLayout
from client.front.main_screen.mission.mission_class import MissionWidget
from PySide6.QtCore import Qt
from client.front.main_screen.ui_main import Ui_MainWidget
from datetime import datetime
import time
import json
from tech_utils.safe_post_req import post_request
from client.front.config import BACK_SERV_PORT, RFD_DOMAIN_NAME, RFD_MM, BASE_CONTROLLERS_LIST, CONTROLLER_PATH
from client.front.state import front_state
from client.front.inputs import DeviceManager

from tech_utils.logger import init_logger
logger = init_logger("FrontMainScreen")

RFD_MM_URL = f"https://{RFD_DOMAIN_NAME}/{RFD_MM}"

def get_missions():
    res = post_request(url=RFD_MM_URL + '/get-missions-list', 
                       payload={"email": front_state.email, "status": "in progress"}, description=f"Get missions list for user {front_state.email}", jwt=front_state.jwt)
    if not res:
        logger.error(f"Can't get missions list for user {front_state.email}")
    else:
        return res['data']


class MainScreen(QWidget):
    def __init__(self, stack: QStackedWidget):
        super().__init__()
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        self.ui.comboBoxControllers.currentTextChanged.connect(self.on_controller_selected)
        self.refresh_device_list()
        self.ui.sliderSensitivity.valueChanged.connect(self.on_sensitivity_changed)
        self.ui.sliderExpo.valueChanged.connect(self.on_expo_changed)
        self.ui.sliderDeadzone.valueChanged.connect(self.on_deadzone_changed)
        self.ui.pushButtonSaveControllerDefaults.clicked.connect(self.save_def_contr_set)
        self.ui.pushButtonRefreshControllers.clicked.connect(self.refresh_device_list)

        self.stack = stack

        self.mission_list = []
        self.mission_widgets = []

        self.ui.pushButtonLaunch.clicked.connect(self.launch_sess)
        self.ui.pushButtonAbort.clicked.connect(self.abort_sess)

    
    def showEvent(self, event):
        super().showEvent(event)

        self.ui.sliderDeadzone.setValue(front_state.deadzone*100*5)
        self.ui.sliderSensitivity.setValue(front_state.sensitivity*50)
        self.ui.sliderExpo.setValue(front_state.expo*100)

        mission_list = get_missions()
        if mission_list != self.mission_list:
            if not mission_list:
                self.append_log("No missions received.")
                logger.warning("No missions received")
                return

            layout = self.ui.scrollAreaWidgetContents.layout()
            if layout is None:
                self.append_log("Error: layout not found")
                logger.error("Layer not found")
                return

            for mission in mission_list:
                if mission not in self.mission_list and mission['status'] == 'in progress':
                    widget = MissionWidget(mission)
                    self.mission_widgets.append(widget)

                    # Оборачиваем в контейнер для центровки и отступа
                    wrapper = QWidget()
                    layout = QHBoxLayout(wrapper)
                    layout.setContentsMargins(0, 0, 0, 20)  # отступ снизу
                    layout.setAlignment(Qt.AlignHCenter)
                    layout.addWidget(widget)

                    self.ui.missionsLayout.addWidget(wrapper)

            self.mission_list = mission_list

    def on_controller_selected(self, controller):
        if front_state.set_controller(controller):
            self.append_log(f"Controller {controller} selected")
        else:
            self.append_log(f"Can't select controller {controller} - invalid value")

    def on_sensitivity_changed(self, value):
        front_state.sensitivity = value / 50. # From 0.0 to 1.0
        front_state.set_controller()
        #self.append_log(f"Sensitivity {front_state.sensitivity} selected")

    def on_expo_changed(self, value):
        front_state.expo = value / 100. # From 0.0 to 1.0
        front_state.set_controller()
        #self.append_log(f"Expo {front_state.expo} selected")

    def on_deadzone_changed(self, value):
        front_state.deadzone = round(value / 100. / 5., 4) # From 0.0 to 0.2
        front_state.set_controller()
        #self.append_log(f"Deadzone {front_state.deadzone} selected")

    def refresh_device_list(self):
        DeviceManager.refresh()
        self.ui.comboBoxControllers.blockSignals(True)
        self.ui.comboBoxControllers.clear()
        self.ui.comboBoxControllers.addItems(DeviceManager.short_names() + BASE_CONTROLLERS_LIST)

        index = self.ui.comboBoxControllers.findText(front_state.controller)
        if index >= 0:
            self.ui.comboBoxControllers.setCurrentIndex(index)

        self.ui.comboBoxControllers.blockSignals(False)


    def save_def_contr_set(self):
        config = {
                "controller": front_state.controller,
                "sensitivity": front_state.sensitivity,
                "expo": front_state.expo,
                "deadzone": front_state.deadzone
            }
        with open(CONTROLLER_PATH, "w") as f:
            json.dump(config, f, indent=2)
        self.append_log(f"Controller {front_state.controller}, sensitivity: {front_state.sensitivity}, expo: {front_state.expo}, deadzone: {front_state.deadzone} have been set as defaults.")

    def append_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui.textEditLog.append(f"[{timestamp}] {message}")
        self.ui.textEditLog.verticalScrollBar().setValue(
            self.ui.textEditLog.verticalScrollBar().maximum()
        )

    def abort_sess(self):
        if front_state.session_id:
            post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-close-session", {"result": 'abort'}, f"Front2Back: {'abort'} session")
            front_state.clear()
        else:
            front_state.main_screen.append_log("No active session to abort")

    def launch_sess(self):
        if front_state.session_id:
            front_state.running_event.set()
            post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-launch-session", {}, "Front2Back: Launch session")
            self.stack.setCurrentIndex(2)
        else:
            front_state.main_screen.append_log("No session to launch")



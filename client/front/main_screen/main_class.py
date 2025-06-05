from PySide6.QtWidgets import QWidget, QStackedWidget, QHBoxLayout
from client.front.main_screen.mission.mission_class import MissionWidget
from PySide6.QtCore import Qt
from client.front.main_screen.ui_main import Ui_MainWidget
from datetime import datetime
import time
from tech_utils.safe_post_req import post_request
from client.front.config import BACK_SERV_PORT, RFD_MM_URL, CONTROLLERS_LIST, CONTROLLER_PATH
from client.front.state import front_state

from tech_utils.logger import init_logger
logger = init_logger("FrontMainScreen")

def get_missions():
    res = post_request(url=RFD_MM_URL + '/get-missions-list', 
                       payload={"user_id": front_state.user_id}, description=f"Get missions list for user {front_state.user_id}")
    if not res:
        logger.error(f"Can't get missions list for user {front_state.user_id}")
    else:
        return res['data']


class MainScreen(QWidget):
    def __init__(self, stack: QStackedWidget):
        super().__init__()
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        self.ui.comboBoxControllers.addItems(CONTROLLERS_LIST)
        self.ui.comboBoxControllers.currentTextChanged.connect(self.on_controller_selected)
        self.ui.sliderSensitivity.valueChanged.connect(self.on_sensitivity_changed)
        self.ui.pushButtonSaveControllerDefaults.clicked.connect(self.save_def_contr_set)
        index = self.ui.comboBoxControllers.findText(front_state.controller)
        if index >= 0:
            self.ui.comboBoxControllers.setCurrentIndex(index)
        self.ui.sliderSensitivity.setValue(front_state.sensitivity*50)

        self.stack = stack

        self.mission_list = []
        self.mission_widgets = []

        self.ui.pushButtonLaunch.clicked.connect(self.launch_sess)
        self.ui.pushButtonAbort.clicked.connect(self.abort_sess)

    
    def showEvent(self, event):
        super().showEvent(event)

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
        front_state.sensitivity = value / 50.

    def save_def_contr_set(self):
        with open(CONTROLLER_PATH, "w") as f:
                f.write(front_state.controller + '\n' + str(front_state.sensitivity))
        self.append_log(f"Controller {front_state.controller} and sensitivity value {front_state.sensitivity} have been set as defaults.")

    def append_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui.textEditLog.append(f"[{timestamp}] {message}")
        self.ui.textEditLog.verticalScrollBar().setValue(
            self.ui.textEditLog.verticalScrollBar().maximum()
        )

    def abort_sess(self):
        if front_state.session_id:
            front_state.abort_event.set()
            post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-close-session", {"result": 'abort'}, f"Front2Back: {'abort'} session")
            time.sleep(0.1)
            front_state.clear()
        else:
            front_state.main_screen.append_log("No active session to abort")

    def launch_sess(self):
        if front_state.session_id:
            post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-launch-session", {}, "Front2Back: Launch session")
            self.stack.setCurrentIndex(2)
        else:
            front_state.main_screen.append_log("No session to launch")



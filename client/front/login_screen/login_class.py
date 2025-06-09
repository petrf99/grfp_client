from PySide6.QtWidgets import QWidget, QStackedWidget
from client.front.login_screen.ui_login import Ui_LoginWidget
from client.front.state import front_state
from tech_utils.logger import init_logger
logger = init_logger("FrontLoginScreen")


class LoginScreen(QWidget):
    def __init__(self, stack: QStackedWidget):
        super().__init__()
        self.ui = Ui_LoginWidget()
        self.stack = stack
        self.ui.setupUi(self)
        self.ui.pushButtonLogin.clicked.connect(self.handle_login)

    def handle_login(self):
        user = self.ui.lineEditUsername.text().strip()
        if user:
            front_state.user_id = user
            self.stack.setCurrentIndex(1)
        else:
            logger.warning("Couldn't get user_id from login screen")

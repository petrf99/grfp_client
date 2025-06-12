import os
import re
import time
import base64
import json
from PySide6.QtWidgets import QWidget, QStackedWidget
from client.front.login_screen.ui_login import Ui_LoginWidget
from client.front.state import front_state
from client.front.config import RFD_DOMAIN_NAME, LOGIN_CREDS_PATH, LOGIN_CREDS_EXPIRE_TMP
from tech_utils.safe_post_req import post_request
from tech_utils.logger import init_logger
logger = init_logger("FrontLoginScreen")

RFD_AUTH_URL = f"https://{RFD_DOMAIN_NAME}/auth"

def decode_jwt_payload(jwt_token: str) -> dict:
    try:
        parts = jwt_token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        payload_b64 = parts[1]

        # Добавим padding, если нужно
        padding = '=' * (-len(payload_b64) % 4)
        payload_b64 += padding

        decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        decoded_str = decoded_bytes.decode('utf-8')
        return json.loads(decoded_str)
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        return {}


class LoginScreen(QWidget):
    def __init__(self, stack: QStackedWidget):
        super().__init__()
        self.ui = Ui_LoginWidget()
        self.stack = stack
        self.ui.setupUi(self)
        self.ui.pushButtonLogin.clicked.connect(self.handle_login)

    def showEvent(self, event):
        super().showEvent(event)
        if os.path.exists(LOGIN_CREDS_PATH):
            try:
                with open(LOGIN_CREDS_PATH, "r") as f:
                    config = json.load(f)
                    email = config.get('email')
                    password = config.get('password')
                    created_at = config.get('created_at')
                    if email and password and created_at and time.time() - created_at < LOGIN_CREDS_EXPIRE_TMP:
                        logger.info("Log-in using saved creds")
                        self.ui.lineEditUsername.setText(email)
                        self.ui.lineEditPassword.setText(password)
                        self.ui.checkBoxSavePassword.setChecked(True)
                    else:
                        self.ui.labelError.setText("Saved credentials expired or invalid.")
                        self.ui.labelError.setStyleSheet("color: gray")
                        self.ui.labelError.setVisible(True)
                        logger.warning("Saved login creds expired or invalid")
                        os.remove(LOGIN_CREDS_PATH)
            except Exception as e:
                logger.warning(f"Failed to auto-fill login: {e}")

    def handle_login(self):
        self.ui.labelError.setVisible(False)
        email = self.ui.lineEditUsername.text().strip()
        password = self.ui.lineEditPassword.text().strip()
        if re.match(r"[^@]+@[^@]+\.[^@]+", email) and password:
            res = post_request(url=RFD_AUTH_URL + '/login', payload={"email": email, "password": password}, description="Login to RFP", retries=1)
            if res:
                jwt = decode_jwt_payload(res.get("jwt"))
                if jwt:
                    front_state.user_id = jwt.get("user_id")
                    front_state.jwt = res.get("jwt")
                    if self.ui.checkBoxSavePassword.isChecked():
                        with open(LOGIN_CREDS_PATH, "w") as f:
                            logger.info("Save login creds to file")
                            config = {"email": email, "password": password, "created_at": time.time()}
                            json.dump(config, f, indent=2)
                    elif os.path.exists(LOGIN_CREDS_PATH):
                        os.remove(LOGIN_CREDS_PATH)
                        logger.info("Login creds file deleted")

                    logger.info(f"User {email} logged in")
                    self.stack.setCurrentIndex(1)
                    return
                else:
                    logger.error("Can't get user_id from JWT")
            else:
                logger.error("Unsuccessfull login request to RFD")
        else:
            logger.error("Failed to get email or password from login screen")
        self.ui.labelError.setText("Invalid email or password")
        self.ui.labelError.setStyleSheet("color: red")
        self.ui.labelError.setVisible(True)

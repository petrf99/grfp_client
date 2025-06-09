from PySide6.QtGui import QImage, QPixmap, QGuiApplication
from PySide6.QtCore import QTimer, Qt, QMetaObject, Slot
from PySide6.QtWidgets import QStackedWidget, QSizePolicy, QApplication
from client.front.flight_screen.ui_flight import Ui_FlightScreen
from client.front.config import FREQUENCY, TELEMETRY_GUI_DRAW_FIELDS, RC_CHANNELS_DEFAULTS, HUD_MARGIN, BACK_SERV_PORT
from client.front.flight_screen.flight_loop.tlmt_listener import telemetry_data, get_telemetry
from client.front.flight_screen.flight_loop.video_listener import get_video
from client.front.logic.back_sender import send_rc_frame
from tech_utils.safe_post_req import post_request
import threading
from client.front.state import front_state
import numpy as np

from PySide6.QtWidgets import QWidget

class FlightScreen(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.ui = Ui_FlightScreen()
        self.ui.setupUi(self)
        self.enable_mouse_tracking(self)
        self.stack = stack

        self.frame = None
        self.telemetry = {}
        self.rc_state = RC_CHANNELS_DEFAULTS.copy()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)

        self.setFocusPolicy(Qt.StrongFocus)  # Позволяет получать события клавиатуры
        self.setMouseTracking(True)  # Чтобы получать mouseMove без нажатия кнопки

        self.ui.labelVideoFrame.setScaledContents(True)
        self.ui.labelVideoFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.telemetry_overlay = TelemetryOverlay(self)
        self.telemetry_overlay.setGeometry(self.rect())
        self.telemetry_overlay.raise_()  # убедиться, что поверх
    
    def showEvent(self, event):
        super().showEvent(event)
        # Launch frame draw
        self.timer.start(1000 // FREQUENCY)  # Frequency FPS
        self.setFocus()
        threading.Thread(target=get_video, daemon=True).start()
        threading.Thread(target=get_telemetry, daemon=True).start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()
        self.frame = None
        self.rc_state = RC_CHANNELS_DEFAULTS.copy()
        self.telemetry = {}

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.telemetry_overlay.setGeometry(self.rect())

    def enable_mouse_tracking(self, widget):
        widget.setMouseTracking(True)
        for child in widget.findChildren(QWidget):
            child.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if front_state.controller == 'mouse_keyboard':
            front_state.rc_input.update_mouse_position(event.pos())


    @Slot()
    def switch_to_screen_1(self):
        self.stack.setCurrentIndex(1)

    def reset_flight_screen(self):
        QMetaObject.invokeMethod(self, "switch_to_screen_1", Qt.QueuedConnection)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            result = 'finish' if front_state.running_event.is_set() else 'abort'
            post_request(f"http://127.0.0.1:{BACK_SERV_PORT}/front-close-session", {"result": result}, f"Front2Back: {result} session")
            self.reset_flight_screen()
            front_state.clear()
        elif front_state.controller in ['keyboard', 'mouse_keyboard']:
            self.rc_state = front_state.rc_input.handle_key_press(event, self.rc_state)

    def keyReleaseEvent(self, event):
        if front_state.controller in ['keyboard', 'mouse_keyboard']:
            front_state.rc_input.handle_key_release(event)


    def set_video_frame(self, frame: np.ndarray):
        self.frame = frame.copy()

    def update_gui(self):
        # Update video frame
        if self.frame is not None:
            image = QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            label_size = self.ui.labelVideoFrame.size()
            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.labelVideoFrame.setPixmap(scaled_pixmap)

        # Upd and send RC data
        self.rc_state = front_state.rc_input.read_frame(self.rc_state)
        send_rc_frame(front_state.session_id, self.rc_state, front_state.controller)

        # 📡 Draw telemetry HUD
        self.telemetry_overlay.update_data()

    def set_video_size(self, size):
        QTimer.singleShot(0, lambda: self._set_video_size(size))

    def _set_video_size(self, size):
        w, h = size  # width, height — в правильном порядке
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen_geometry.width(), screen_geometry.height()

        video_w, video_h = size
        # Масштабируем под экран, если нужно
        scale = min(screen_w / video_w, screen_h / video_h, 1.0)
        w, h = int(video_w * scale), int(video_h * scale)

        self.ui.labelVideoFrame.setMinimumSize(w, h)
        self.ui.labelVideoFrame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.ui.labelVideoFrame.setScaledContents(False)
        self.setMinimumSize(w, h)
        self.setMaximumSize(screen_geometry.size())

        # Найти QStackedWidget и адаптировать его размер
        parent = self.parent()
        while parent and not isinstance(parent, QStackedWidget):
            parent = parent.parent()

        if parent:
            QTimer.singleShot(0, lambda: parent.adjustSize())


from PySide6.QtGui import QPainter, QColor, QFont

class TelemetryOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setVisible(True)

    def update_data(self):
        self.update()  # triggers paintEvent()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12))

        hud_margin = HUD_MARGIN
        y = hud_margin

        painter.drawText(hud_margin, y, "You are in the Flight Mode. Press ESC to exit")
        y += 20

        global telemetry_data
        if not telemetry_data:
            return
        else:
            tlmt_values = telemetry_data.copy()

        for k, v in tlmt_values.items():
            if k in TELEMETRY_GUI_DRAW_FIELDS + ["round_trip_time_ms"]:
                if isinstance(v, dict):
                    painter.drawText(hud_margin, y, f"{k}")
                    y += 20
                    for k_, v_ in v.items():
                        painter.drawText(hud_margin, y, f" - {k_}: {v_}")
                        y += 20
                else:
                    painter.drawText(hud_margin, y, f"{k}: {v}")
                    y += 20

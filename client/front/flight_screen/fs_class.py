from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QStackedWidget, QSizePolicy
from client.front.flight_screen.ui_flight import Ui_FlightScreen
from client.front.config import FREQUENCY, TELEMETRY_GUI_DRAW_FIELDS
from client.front.logic.data_listeners import telemetry_data
import numpy as np

from PySide6.QtWidgets import QWidget

class FlightScreen(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.ui = Ui_FlightScreen()
        self.ui.setupUi(self)
        self.stack = stack

        self.frame = None
        self.telemetry = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(1000 // FREQUENCY)  # Frequency FPS

        self.ui.labelVideoFrame.setScaledContents(True)
        self.ui.labelVideoFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.telemetry_overlay = TelemetryOverlay(self)
        self.telemetry_overlay.setGeometry(self.rect())
        self.telemetry_overlay.raise_()  # убедиться, что поверх

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.telemetry_overlay.setGeometry(self.rect())

    def set_video_frame(self, frame: np.ndarray):
        self.frame = frame.copy()

    def set_telemetry_data(self, telemetry: dict):
        self.telemetry = telemetry

    def update_gui(self):
        if self.frame is not None:
            image = QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.ui.labelVideoFrame.setPixmap(pixmap)

        # Отрисовать HUD поверх — можно будет сделать QLabel поверх QLabel
        # или QPainter прямо на pixmap — если нужно покажу как.

    def set_video_size(self, size):
        h, w = size

        self.ui.labelVideoFrame.setMinimumSize(w, h)
        self.ui.labelVideoFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.labelVideoFrame.setScaledContents(True)
        self.setMinimumSize(w, h)

        # Найти QStackedWidget
        parent = self.parent()
        while parent and not isinstance(parent, QStackedWidget):
            parent = parent.parent()

        if parent:
            QTimer.singleShot(0, lambda: parent.resize(w, h))



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
        global telemetry_data
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12))

        y = 20
        for key, value in telemetry_data.items():
            if key in TELEMETRY_GUI_DRAW_FIELDS:
                painter.drawText(10, y, f"{key}: {value}")
                y += 20

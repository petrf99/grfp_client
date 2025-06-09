# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'flight_screen.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_FlightScreen(object):
    def setupUi(self, FlightScreen):
        if not FlightScreen.objectName():
            FlightScreen.setObjectName(u"FlightScreen")
        FlightScreen.resize(960, 540)
        self.verticalLayout = QVBoxLayout(FlightScreen)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelVideoFrame = QLabel(FlightScreen)
        self.labelVideoFrame.setObjectName(u"labelVideoFrame")
        self.labelVideoFrame.setMinimumSize(QSize(640, 360))
        self.labelVideoFrame.setAlignment(Qt.AlignCenter)
        self.labelVideoFrame.setStyleSheet(u"background-color: black; color: white;")

        self.verticalLayout.addWidget(self.labelVideoFrame)


        self.retranslateUi(FlightScreen)

        QMetaObject.connectSlotsByName(FlightScreen)
    # setupUi

    def retranslateUi(self, FlightScreen):
        FlightScreen.setWindowTitle(QCoreApplication.translate("FlightScreen", u"Video Stream", None))
        self.labelVideoFrame.setText(QCoreApplication.translate("FlightScreen", u"Video frame will appear here", None))
    # retranslateUi


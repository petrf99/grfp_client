# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_screen.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QScrollArea,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        if not MainWidget.objectName():
            MainWidget.setObjectName(u"MainWidget")
        MainWidget.resize(600, 500)
        self.verticalLayout = QVBoxLayout(MainWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(MainWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.missionsLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.missionsLayout.setObjectName(u"missionsLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.controlLayout = QHBoxLayout()
        self.controlLayout.setObjectName(u"controlLayout")
        self.pushButtonLaunch = QPushButton(MainWidget)
        self.pushButtonLaunch.setObjectName(u"pushButtonLaunch")

        self.controlLayout.addWidget(self.pushButtonLaunch)

        self.pushButtonAbort = QPushButton(MainWidget)
        self.pushButtonAbort.setObjectName(u"pushButtonAbort")

        self.controlLayout.addWidget(self.pushButtonAbort)


        self.verticalLayout.addLayout(self.controlLayout)

        self.textEditLog = QTextEdit(MainWidget)
        self.textEditLog.setObjectName(u"textEditLog")
        self.textEditLog.setReadOnly(True)

        self.verticalLayout.addWidget(self.textEditLog)


        self.retranslateUi(MainWidget)

        QMetaObject.connectSlotsByName(MainWidget)
    # setupUi

    def retranslateUi(self, MainWidget):
        MainWidget.setWindowTitle(QCoreApplication.translate("MainWidget", u"Mission Control", None))
        self.pushButtonLaunch.setText(QCoreApplication.translate("MainWidget", u"Launch Session", None))
        self.pushButtonAbort.setText(QCoreApplication.translate("MainWidget", u"Abort Session", None))
        self.textEditLog.setPlaceholderText(QCoreApplication.translate("MainWidget", u"System messages will appear here\u2026", None))
    # retranslateUi


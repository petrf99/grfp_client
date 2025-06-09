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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QSlider,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

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

        self.controllerSetupRow = QHBoxLayout()
        self.controllerSetupRow.setObjectName(u"controllerSetupRow")
        self.controllerLayout = QHBoxLayout()
        self.controllerLayout.setObjectName(u"controllerLayout")
        self.labelController = QLabel(MainWidget)
        self.labelController.setObjectName(u"labelController")

        self.controllerLayout.addWidget(self.labelController)

        self.comboBoxControllers = QComboBox(MainWidget)
        self.comboBoxControllers.setObjectName(u"comboBoxControllers")

        self.controllerLayout.addWidget(self.comboBoxControllers)

        self.pushButtonRefreshControllers = QPushButton(MainWidget)
        self.pushButtonRefreshControllers.setObjectName(u"pushButtonRefreshControllers")
        self.pushButtonRefreshControllers.setMaximumWidth(80)

        self.controllerLayout.addWidget(self.pushButtonRefreshControllers)


        self.controllerSetupRow.addLayout(self.controllerLayout)

        self.horizontalSpacer1 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controllerSetupRow.addItem(self.horizontalSpacer1)

        self.sensitivityGroupLayout = QHBoxLayout()
        self.sensitivityGroupLayout.setObjectName(u"sensitivityGroupLayout")
        self.labelSensitivity = QLabel(MainWidget)
        self.labelSensitivity.setObjectName(u"labelSensitivity")

        self.sensitivityGroupLayout.addWidget(self.labelSensitivity)

        self.sliderSensitivity = QSlider(MainWidget)
        self.sliderSensitivity.setObjectName(u"sliderSensitivity")
        self.sliderSensitivity.setOrientation(Qt.Horizontal)
        self.sliderSensitivity.setMinimum(1)
        self.sliderSensitivity.setMaximum(100)
        self.sliderSensitivity.setMinimumWidth(120)
        self.sliderSensitivity.setMaximumWidth(120)

        self.sensitivityGroupLayout.addWidget(self.sliderSensitivity)


        self.controllerSetupRow.addLayout(self.sensitivityGroupLayout)

        self.expoGroupLayout = QHBoxLayout()
        self.expoGroupLayout.setObjectName(u"expoGroupLayout")
        self.labelExpo = QLabel(MainWidget)
        self.labelExpo.setObjectName(u"labelExpo")

        self.expoGroupLayout.addWidget(self.labelExpo)

        self.sliderExpo = QSlider(MainWidget)
        self.sliderExpo.setObjectName(u"sliderExpo")
        self.sliderExpo.setOrientation(Qt.Horizontal)
        self.sliderExpo.setMinimum(0)
        self.sliderExpo.setMaximum(100)
        self.sliderExpo.setMinimumWidth(120)
        self.sliderExpo.setMaximumWidth(120)

        self.expoGroupLayout.addWidget(self.sliderExpo)


        self.controllerSetupRow.addLayout(self.expoGroupLayout)

        self.deadzoneGroupLayout = QHBoxLayout()
        self.deadzoneGroupLayout.setObjectName(u"deadzoneGroupLayout")
        self.labelDeadzone = QLabel(MainWidget)
        self.labelDeadzone.setObjectName(u"labelDeadzone")

        self.deadzoneGroupLayout.addWidget(self.labelDeadzone)

        self.sliderDeadzone = QSlider(MainWidget)
        self.sliderDeadzone.setObjectName(u"sliderDeadzone")
        self.sliderDeadzone.setOrientation(Qt.Horizontal)
        self.sliderDeadzone.setMinimum(0)
        self.sliderDeadzone.setMaximum(100)
        self.sliderDeadzone.setMinimumWidth(120)
        self.sliderDeadzone.setMaximumWidth(120)

        self.deadzoneGroupLayout.addWidget(self.sliderDeadzone)


        self.controllerSetupRow.addLayout(self.deadzoneGroupLayout)

        self.horizontalSpacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controllerSetupRow.addItem(self.horizontalSpacer2)

        self.pushButtonSaveControllerDefaults = QPushButton(MainWidget)
        self.pushButtonSaveControllerDefaults.setObjectName(u"pushButtonSaveControllerDefaults")
        self.pushButtonSaveControllerDefaults.setMaximumWidth(130)

        self.controllerSetupRow.addWidget(self.pushButtonSaveControllerDefaults)


        self.verticalLayout.addLayout(self.controllerSetupRow)

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
        self.labelController.setText(QCoreApplication.translate("MainWidget", u"Controller:", None))
        self.pushButtonRefreshControllers.setText(QCoreApplication.translate("MainWidget", u"Refresh", None))
        self.labelSensitivity.setText(QCoreApplication.translate("MainWidget", u"Sensitivity:", None))
        self.labelExpo.setText(QCoreApplication.translate("MainWidget", u"Expo:", None))
        self.labelDeadzone.setText(QCoreApplication.translate("MainWidget", u"Deadzone:", None))
        self.pushButtonSaveControllerDefaults.setText(QCoreApplication.translate("MainWidget", u"Save as default", None))
        self.textEditLog.setPlaceholderText(QCoreApplication.translate("MainWidget", u"System messages will appear here\u2026", None))
    # retranslateUi


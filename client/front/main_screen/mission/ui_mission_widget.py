# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mission_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_MissionWidget(object):
    def setupUi(self, MissionWidget):
        if not MissionWidget.objectName():
            MissionWidget.setObjectName(u"MissionWidget")
        MissionWidget.setMinimumSize(QSize(0, 120))
        MissionWidget.setMaximumWidth(800)
        self.mainLayout = QVBoxLayout(MissionWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelDroneType = QLabel(MissionWidget)
        self.labelDroneType.setObjectName(u"labelDroneType")

        self.gridLayout.addWidget(self.labelDroneType, 0, 0, 1, 1)

        self.labelLocation = QLabel(MissionWidget)
        self.labelLocation.setObjectName(u"labelLocation")

        self.gridLayout.addWidget(self.labelLocation, 0, 1, 1, 1)

        self.labelMissionGroup = QLabel(MissionWidget)
        self.labelMissionGroup.setObjectName(u"labelMissionGroup")

        self.gridLayout.addWidget(self.labelMissionGroup, 1, 0, 1, 1)

        self.labelStatus = QLabel(MissionWidget)
        self.labelStatus.setObjectName(u"labelStatus")

        self.gridLayout.addWidget(self.labelStatus, 1, 1, 1, 1)

        self.labelTimeWindow = QLabel(MissionWidget)
        self.labelTimeWindow.setObjectName(u"labelTimeWindow")

        self.gridLayout.addWidget(self.labelTimeWindow, 2, 0, 1, 2)

        self.labelMissionId = QLabel(MissionWidget)
        self.labelMissionId.setObjectName(u"labelMissionId")

        self.gridLayout.addWidget(self.labelMissionId, 3, 0, 1, 2)


        self.mainLayout.addLayout(self.gridLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.spacerLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.spacerLeft)

        self.pushButtonConnect = QPushButton(MissionWidget)
        self.pushButtonConnect.setObjectName(u"pushButtonConnect")

        self.buttonLayout.addWidget(self.pushButtonConnect)

        self.spacerRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.spacerRight)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(MissionWidget)

        QMetaObject.connectSlotsByName(MissionWidget)
    # setupUi

    def retranslateUi(self, MissionWidget):
        self.labelDroneType.setText(QCoreApplication.translate("MissionWidget", u"Drone: quad-fpv", None))
        self.labelLocation.setText(QCoreApplication.translate("MissionWidget", u"Location: Asuncion", None))
        self.labelMissionGroup.setText(QCoreApplication.translate("MissionWidget", u"Group: default", None))
        self.labelStatus.setText(QCoreApplication.translate("MissionWidget", u"Status: in progress", None))
        self.labelTimeWindow.setText(QCoreApplication.translate("MissionWidget", u"Time Window: 14:00-15:00 UTC", None))
        self.labelMissionId.setText(QCoreApplication.translate("MissionWidget", u"ID: 4505bfee-xxxx-xxxx", None))
        self.pushButtonConnect.setText(QCoreApplication.translate("MissionWidget", u"Connect", None))
        pass
    # retranslateUi


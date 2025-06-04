# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_screen.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_LoginWidget(object):
    def setupUi(self, LoginWidget):
        if not LoginWidget.objectName():
            LoginWidget.setObjectName(u"LoginWidget")
        LoginWidget.resize(300, 150)
        self.formLayout = QFormLayout(LoginWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.labelUsername = QLabel(LoginWidget)
        self.labelUsername.setObjectName(u"labelUsername")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelUsername)

        self.lineEditUsername = QLineEdit(LoginWidget)
        self.lineEditUsername.setObjectName(u"lineEditUsername")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditUsername)

        self.labelPassword = QLabel(LoginWidget)
        self.labelPassword.setObjectName(u"labelPassword")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPassword)

        self.lineEditPassword = QLineEdit(LoginWidget)
        self.lineEditPassword.setObjectName(u"lineEditPassword")
        self.lineEditPassword.setEchoMode(QLineEdit.Password)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditPassword)

        self.pushButtonLogin = QPushButton(LoginWidget)
        self.pushButtonLogin.setObjectName(u"pushButtonLogin")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.pushButtonLogin)


        self.retranslateUi(LoginWidget)

        QMetaObject.connectSlotsByName(LoginWidget)
    # setupUi

    def retranslateUi(self, LoginWidget):
        LoginWidget.setWindowTitle(QCoreApplication.translate("LoginWidget", u"Login", None))
        self.labelUsername.setText(QCoreApplication.translate("LoginWidget", u"Username:", None))
        self.labelPassword.setText(QCoreApplication.translate("LoginWidget", u"Password:", None))
        self.pushButtonLogin.setText(QCoreApplication.translate("LoginWidget", u"Login", None))
    # retranslateUi


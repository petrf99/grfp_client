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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_LoginWidget(object):
    def setupUi(self, LoginWidget):
        if not LoginWidget.objectName():
            LoginWidget.setObjectName(u"LoginWidget")
        LoginWidget.resize(300, 200)
        self.verticalLayout = QVBoxLayout(LoginWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacerTop = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacerTop)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.labelEmail = QLabel(LoginWidget)
        self.labelEmail.setObjectName(u"labelEmail")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelEmail)

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

        self.checkBoxSavePassword = QCheckBox(LoginWidget)
        self.checkBoxSavePassword.setObjectName(u"checkBoxSavePassword")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.checkBoxSavePassword)

        self.pushButtonLogin = QPushButton(LoginWidget)
        self.pushButtonLogin.setObjectName(u"pushButtonLogin")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.pushButtonLogin)


        self.verticalLayout.addLayout(self.formLayout)

        self.labelError = QLabel(LoginWidget)
        self.labelError.setObjectName(u"labelError")
        self.labelError.setVisible(False)
        self.labelError.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.labelError)

        self.verticalSpacerBottom = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacerBottom)


        self.retranslateUi(LoginWidget)

        QMetaObject.connectSlotsByName(LoginWidget)
    # setupUi

    def retranslateUi(self, LoginWidget):
        LoginWidget.setWindowTitle(QCoreApplication.translate("LoginWidget", u"Login", None))
        self.labelEmail.setText(QCoreApplication.translate("LoginWidget", u"Email:", None))
        self.labelPassword.setText(QCoreApplication.translate("LoginWidget", u"Password:", None))
        self.checkBoxSavePassword.setText(QCoreApplication.translate("LoginWidget", u"Save password", None))
        self.pushButtonLogin.setText(QCoreApplication.translate("LoginWidget", u"Login", None))
        self.labelError.setText("")
        self.labelError.setStyleSheet(QCoreApplication.translate("LoginWidget", u"color: red", None))
    # retranslateUi


# pylint: skip-file
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

from ui.compiled import resources_rc

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        if not Preferences.objectName():
            Preferences.setObjectName(u"Preferences")
        Preferences.setWindowModality(Qt.ApplicationModal)
        Preferences.resize(400, 300)
        icon = QIcon()
        icon.addFile(u":/images/gear.png", QSize(), QIcon.Normal, QIcon.Off)
        Preferences.setWindowIcon(icon)
        self.horizontalLayout = QHBoxLayout(Preferences)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.preferences_list = QListWidget(Preferences)
        QListWidgetItem(self.preferences_list)
        QListWidgetItem(self.preferences_list)
        self.preferences_list.setObjectName(u"preferences_list")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preferences_list.sizePolicy().hasHeightForWidth())
        self.preferences_list.setSizePolicy(sizePolicy)
        self.preferences_list.setMinimumSize(QSize(100, 0))
        self.preferences_list.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.preferences_list)

        self.detail_widget = QWidget(Preferences)
        self.detail_widget.setObjectName(u"detail_widget")
        self.detail_widget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.detail_widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.horizontalLayout.addWidget(self.detail_widget)


        self.retranslateUi(Preferences)

        QMetaObject.connectSlotsByName(Preferences)
    # setupUi

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QCoreApplication.translate("Preferences", u"Preferences", None))

        __sortingEnabled = self.preferences_list.isSortingEnabled()
        self.preferences_list.setSortingEnabled(False)
        ___qlistwidgetitem = self.preferences_list.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Preferences", u"General", None));
        ___qlistwidgetitem1 = self.preferences_list.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("Preferences", u"Qemu Hosts", None));
        self.preferences_list.setSortingEnabled(__sortingEnabled)

    # retranslateUi


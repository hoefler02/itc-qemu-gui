# pylint: skip-file
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        icon = QIcon()
        icon.addFile(u":/images/qemu.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionOther_Windows = QAction(MainWindow)
        self.actionOther_Windows.setObjectName(u"actionOther_Windows")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionQMP_Reference = QAction(MainWindow)
        self.actionQMP_Reference.setObjectName(u"actionQMP_Reference")
        self.actionDump_Schema = QAction(MainWindow)
        self.actionDump_Schema.setObjectName(u"actionDump_Schema")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.browser_tab = QTabWidget(self.centralwidget)
        self.browser_tab.setObjectName(u"browser_tab")
        self.browser_tab.setEnabled(True)
        self.cmd_tab = QWidget()
        self.cmd_tab.setObjectName(u"cmd_tab")
        self.horizontalLayout = QHBoxLayout(self.cmd_tab)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.cmd_search_field = QLineEdit(self.cmd_tab)
        self.cmd_search_field.setObjectName(u"cmd_search_field")

        self.horizontalLayout_5.addWidget(self.cmd_search_field)

        self.cmd_search_btn = QPushButton(self.cmd_tab)
        self.cmd_search_btn.setObjectName(u"cmd_search_btn")

        self.horizontalLayout_5.addWidget(self.cmd_search_btn)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)

        self.cmd_list = QListWidget(self.cmd_tab)
        self.cmd_list.setObjectName(u"cmd_list")

        self.verticalLayout_5.addWidget(self.cmd_list)


        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.cmd_detail = QTreeWidget(self.cmd_tab)
        self.cmd_detail.setObjectName(u"cmd_detail")

        self.verticalLayout.addWidget(self.cmd_detail)

        self.build_cmd_btn = QPushButton(self.cmd_tab)
        self.build_cmd_btn.setObjectName(u"build_cmd_btn")
        self.build_cmd_btn.setEnabled(False)

        self.verticalLayout.addWidget(self.build_cmd_btn)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.browser_tab.addTab(self.cmd_tab, "")
        self.event_tab = QWidget()
        self.event_tab.setObjectName(u"event_tab")
        self.horizontalLayout_2 = QHBoxLayout(self.event_tab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.event_search_field = QLineEdit(self.event_tab)
        self.event_search_field.setObjectName(u"event_search_field")

        self.horizontalLayout_4.addWidget(self.event_search_field)

        self.event_search_btn = QPushButton(self.event_tab)
        self.event_search_btn.setObjectName(u"event_search_btn")

        self.horizontalLayout_4.addWidget(self.event_search_btn)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.event_list = QListWidget(self.event_tab)
        self.event_list.setObjectName(u"event_list")

        self.verticalLayout_4.addWidget(self.event_list)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.event_detail = QTreeWidget(self.event_tab)
        self.event_detail.setObjectName(u"event_detail")

        self.verticalLayout_3.addWidget(self.event_detail)

        self.build_event_btn = QPushButton(self.event_tab)
        self.build_event_btn.setObjectName(u"build_event_btn")
        self.build_event_btn.setEnabled(False)

        self.verticalLayout_3.addWidget(self.build_event_btn)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.browser_tab.addTab(self.event_tab, "")

        self.verticalLayout_2.addWidget(self.browser_tab)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 25))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionDump_Schema)
        self.menuEdit.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionQMP_Reference)
        self.menuView.addAction(self.actionOther_Windows)

        self.retranslateUi(MainWindow)

        self.browser_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Qemu", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionOther_Windows.setText(QCoreApplication.translate("MainWindow", u"Other Windows", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionQMP_Reference.setText(QCoreApplication.translate("MainWindow", u"QMP Reference", None))
        self.actionDump_Schema.setText(QCoreApplication.translate("MainWindow", u"Dump Schema", None))
#if QT_CONFIG(tooltip)
        self.actionDump_Schema.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Save the QMP Schema data to a JSON file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmd_search_btn.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        ___qtreewidgetitem = self.cmd_detail.headerItem()
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("MainWindow", u"Values", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Data Type", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Meta Type", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Optional", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Member", None));
        self.build_cmd_btn.setText(QCoreApplication.translate("MainWindow", u"Build Command", None))
        self.browser_tab.setTabText(self.browser_tab.indexOf(self.cmd_tab), QCoreApplication.translate("MainWindow", u"Command Browser", None))
        self.event_search_btn.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        ___qtreewidgetitem1 = self.event_detail.headerItem()
        ___qtreewidgetitem1.setText(4, QCoreApplication.translate("MainWindow", u"Values", None));
        ___qtreewidgetitem1.setText(3, QCoreApplication.translate("MainWindow", u"Data Type", None));
        ___qtreewidgetitem1.setText(2, QCoreApplication.translate("MainWindow", u"Meta Type", None));
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Optional", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Member", None));
        self.build_event_btn.setText(QCoreApplication.translate("MainWindow", u"Build Event", None))
        self.browser_tab.setTabText(self.browser_tab.indexOf(self.event_tab), QCoreApplication.translate("MainWindow", u"Event Browser", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
    # retranslateUi


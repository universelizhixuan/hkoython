# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from queue import Queue
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsPixmapItem



class Ui_MainWindow(object):

    def setupUi(self, MainWindow:QMainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2560, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(340, 10, 198, 28))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(1160, 10, 156, 28))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setKerning(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1970, 10, 156, 28))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setKerning(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(60, 51, 2436, 454))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.graphicsView_1 = QtWidgets.QGraphicsView(self.splitter)
        self.graphicsView_1.setObjectName("graphicsView_1")
        self.graphicsView_2 = QtWidgets.QGraphicsView(self.splitter)
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.graphicsView_3 = QtWidgets.QGraphicsView(self.splitter)
        self.graphicsView_3.setObjectName("graphicsView_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2560, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menunormal_1 = QtWidgets.QMenu(self.menu_2)
        self.menunormal_1.setObjectName("menunormal_1")
        self.menuptz_1 = QtWidgets.QMenu(self.menu_2)
        self.menuptz_1.setObjectName("menuptz_1")
        self.menuptz_2 = QtWidgets.QMenu(self.menu_2)
        self.menuptz_2.setObjectName("menuptz_2")
        MainWindow.setMenuBar(self.menubar)
        self.actionposture = QtWidgets.QAction(MainWindow)
        self.actionposture.setObjectName("actionposture")
        self.actionbegin_1 = QtWidgets.QAction(MainWindow)
        self.actionbegin_1.setCheckable(True)
        self.actionbegin_1.setChecked(False)
        self.actionbegin_1.setObjectName("actionbegin_1")
        self.actionend_1 = QtWidgets.QAction(MainWindow)
        self.actionend_1.setCheckable(True)
        self.actionend_1.setObjectName("actionend_1")
        self.actionbegin_2 = QtWidgets.QAction(MainWindow)
        self.actionbegin_2.setCheckable(True)
        self.actionbegin_2.setChecked(False)
        self.actionbegin_2.setObjectName("actionbegin_2")
        self.actionend_2 = QtWidgets.QAction(MainWindow)
        self.actionend_2.setCheckable(True)
        self.actionend_2.setObjectName("actionend_2")
        self.actionbegin_3 = QtWidgets.QAction(MainWindow)
        self.actionbegin_3.setCheckable(True)
        self.actionbegin_3.setChecked(False)
        self.actionbegin_3.setObjectName("actionbegin_3")
        self.actionend_3 = QtWidgets.QAction(MainWindow)
        self.actionend_3.setCheckable(True)
        self.actionend_3.setObjectName("actionend_3")
        self.menunormal_1.addAction(self.actionbegin_1)
        self.menuptz_1.addAction(self.actionbegin_2)
        self.menuptz_2.addAction(self.actionbegin_3)
        self.menu_2.addAction(self.menunormal_1.menuAction())
        self.menu_2.addAction(self.menuptz_1.menuAction())
        self.menu_2.addAction(self.menuptz_2.menuAction())
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())



        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "姿态监测(normal-1)"))
        self.label_2.setText(_translate("MainWindow", "安装监测(ptz-1)"))
        self.label_3.setText(_translate("MainWindow", "安装监测(ptz-2)"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.menu_2.setTitle(_translate("MainWindow", "监控"))
        self.menunormal_1.setTitle(_translate("MainWindow", "normal-1"))
        self.menuptz_1.setTitle(_translate("MainWindow", "ptz-1"))
        self.menuptz_2.setTitle(_translate("MainWindow", "ptz-2"))
        self.actionposture.setText(_translate("MainWindow", "posture"))
        self.actionbegin_1.setText(_translate("MainWindow", "begin/end"))
        self.actionend_1.setText(_translate("MainWindow", "end"))
        self.actionbegin_2.setText(_translate("MainWindow", "begin/end"))
        self.actionend_2.setText(_translate("MainWindow", "end"))
        self.actionbegin_3.setText(_translate("MainWindow", "begin/end"))
        self.actionend_3.setText(_translate("MainWindow", "end"))


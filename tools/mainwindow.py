import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from tools.graphics import Graphics

def gen_mainwindow(mixed_q_dict):
    app = QtWidgets.QApplication(sys.argv)
    myshow = Graphics(mixed_q_dict)
    myshow.show()
    app.exec_()

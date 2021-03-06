import sys
from PyQt5 import QtWidgets
from tools.graphics import Graphics


def gen_mainwindow(mixed_q_dict, im_seg, mask_path):
    app = QtWidgets.QApplication(sys.argv)
    myshow = Graphics(mixed_q_dict, im_seg, mask_path)
    myshow.show()
    app.exec_()

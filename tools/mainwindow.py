import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from tools.graphics import Graphics
from queue import Queue
from tools.imseg import ImSeg

def gen_mainwindow(mixed_q_dict,im_seg, mask_path):
    app = QtWidgets.QApplication(sys.argv)
    myshow = Graphics(mixed_q_dict, im_seg, mask_path)
    myshow.show()
    app.exec_()
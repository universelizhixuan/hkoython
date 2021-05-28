import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from tools.graphics import Graphics
from queue import Queue

def gen_mainwindow(mixed_q_dict,im_seg, mask_path):
    app = QtWidgets.QApplication(sys.argv)
    myshow = Graphics(mixed_q_dict, im_seg, mask_path)
    myshow.show()
    app.exec_()

if __name__ == '__main__':
    pass
    # gen_mainwindow({'normal-1':Queue(),'ptz-1':Queue(),'ptz-2':Queue()})
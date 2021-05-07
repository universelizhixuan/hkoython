from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import cv2
from .ui_mainwindow import Ui_MainWindow
from queue import Queue
from threading import Thread

class Graphics(QMainWindow,Ui_MainWindow):
    def __init__(self,mixed_q_dict:dict, parent=None):
        super(Graphics, self).__init__(parent)
        self.setupUi(self)
        # 把mixed_q区分开
        self.graphicsView_1_q = None
        self.graphicsView_2_q = None
        self.graphicsView_3_q = None
        self.gen_graphics_q(mixed_q_dict)
        # 利用QTimer触发刷新机制
        self.timer1 = QTimer()
        self.timer2 = QTimer()
        self.timer3 = QTimer()
        # 创建场景
        self.scene_1 = QGraphicsScene()
        self.scene_2 = QGraphicsScene()
        self.scene_3 = QGraphicsScene()
        # 利用menu菜单触发timer
        self.actionbegin_1.toggled.connect(self.graphicsView1_toggled)
        self.actionbegin_2.toggled.connect(self.graphicsView2_toggled)
        self.actionbegin_3.toggled.connect(self.graphicsView3_toggled)
        # 绑定计时器feedback函数
        self.timer1.timeout.connect(self.timeout1)
        self.timer2.timeout.connect(self.timeout2)
        self.timer3.timeout.connect(self.timeout3)


    def gen_graphics_q(self,mixed_q_dict):
        self.graphicsView_1_q = mixed_q_dict['normal-1']
        self.graphicsView_2_q = mixed_q_dict['ptz-1']
        self.graphicsView_3_q = mixed_q_dict['ptz-2']


    def graphicsView1_toggled(self):
        if self.actionbegin_1.isChecked():
            self.timer1.setInterval(500)
            self.timer1.start()
        else:
            self.timer1.stop()
    def graphicsView2_toggled(self):
        if self.actionbegin_2.isChecked():
            self.timer2.setInterval(500)
            self.timer2.start()
        else:
            self.timer2.stop()
    def graphicsView3_toggled(self):
        if self.actionbegin_3.isChecked():
            self.timer3.setInterval(500)
            self.timer3.start()
        else:
            self.timer3.stop()

    def timeout1(self):
        if self.graphicsView_1_q.qsize() != 0:
            path = self.graphicsView_1_q.get()
            print(path)
            img = cv2.imread(path)  # 读取图像
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
            x = img.shape[1]  # 获取图像大小
            y = img.shape[0]
            zoomscale = 0.313  # 图片放缩尺度
            frame = QImage(img, x, y, QImage.Format_RGB888)
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)  # 创建像素图元
            item.setScale(zoomscale)
            scene = QGraphicsScene()  # 创建场景
            scene.addItem(item)
            self.graphicsView_1.setScene(scene)  # 将场景添加至视图
            self.graphicsView_1.viewport().update()
    def timeout2(self):
        if self.graphicsView_2_q.qsize() != 0:
            path = self.graphicsView_2_q.get()
            print(path)
            img = cv2.imread(path)  # 读取图像
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
            x = img.shape[1]  # 获取图像大小
            y = img.shape[0]
            zoomscale = 0.418  # 图片放缩尺度
            frame = QImage(img, x, y, QImage.Format_RGB888)
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)  # 创建像素图元
            item.setScale(zoomscale)
            scene = QGraphicsScene()  # 创建场景
            scene.addItem(item)
            self.graphicsView_2.setScene(scene)  # 将场景添加至视图
            self.graphicsView_2.viewport().update()
    def timeout3(self):
        if self.graphicsView_3_q.qsize() != 0:
            path = self.graphicsView_3_q.get()
            print(path)
            img = cv2.imread(path)  # 读取图像
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
            x = img.shape[1]  # 获取图像大小
            y = img.shape[0]
            zoomscale = 0.313  # 图片放缩尺度
            frame = QImage(img, x, y, QImage.Format_RGB888)
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)  # 创建像素图元
            item.setScale(zoomscale)
            scene = QGraphicsScene()  # 创建场景
            scene.addItem(item)
            self.graphicsView_3.setScene(scene)  # 将场景添加至视图
            self.graphicsView_3.viewport().update()

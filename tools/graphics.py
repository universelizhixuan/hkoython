from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import cv2
from .ui_mainwindow import Ui_MainWindow
from queue import Queue
from threading import Thread
from tools.imseg import ImSeg
import os
import numpy as np

class Graphics(QMainWindow,Ui_MainWindow):
    def __init__(self,mixed_q_dict:dict, im_seg:ImSeg, mask_path:str, parent=None):
        super(Graphics, self).__init__(parent)
        self.setupUi(self)
        # 保存mask的根目录
        self.mask_path = mask_path
        # 把mixed_q区分开
        self.graphicsView_1_q = None
        self.graphicsView_2_q = None
        self.graphicsView_3_q = None
        self.gen_graphics_q(mixed_q_dict)
        # 将im_seg传入GUI做交互
        self.im_seg = im_seg
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
        # collect菜单中的begin/end绑定im_seg中的envelope_event
        self.actionbegin_4.toggled.connect(self.envelope_sign)
        # collect菜单中的save，存储envelope_array和outline_array
        self.actionsave.triggered.connect(self.save_array)
        # collect菜单中的call，调用envelope_array和outline_array
        self.actioncall.triggered.connect(self.call_array)
        # collect菜单中的clear，清除im_seg中的envelop_array
        self.actionclear.triggered.connect(self.clear_array)

        # 绑定计时器feedback函数
        self.timer1.timeout.connect(self.timeout1)
        self.timer2.timeout.connect(self.timeout2)
        self.timer3.timeout.connect(self.timeout3)
        # 包络(envelope)掩码文件路径，初始为None
        self.envelope_mask_path = None
        # 轮廓(outline)掩码文件路径，初始为None
        self.outline_mask_path = None
        # judge_mask函数的线程
        self.judge_mask_thread = None


    def gen_graphics_q(self,mixed_q_dict):
        self.graphicsView_1_q = mixed_q_dict['normal-1']
        self.graphicsView_2_q = mixed_q_dict['ptz-1']
        self.graphicsView_3_q = mixed_q_dict['ptz-2']


    def graphicsView1_toggled(self):
        if self.actionbegin_1.isChecked():
            if self.envelope_mask_path and self.outline_mask_path:
                self.judge_mask_thread = Thread(target=self.im_seg.judge_mask,args=(self.envelope_mask_path,self.outline_mask_path,50))
                self.judge_mask_thread.start()
                self.timer1.setInterval(500)
                self.timer1.start()
            else:
                QMessageBox.question(self, '提醒', '请先调用轮廓掩码',QMessageBox.Yes)
                self.actionbegin_1.setChecked(False)
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

    def envelope_sign(self):
        if self.actionbegin_3.isChecked():
            self.im_seg.envelope_event.set()
            self.actionbegin_1.setChecked(False)
        else:
            self.im_seg.envelope_event.clear()

    def save_array(self):
        # ==>('D:/1111.txt', 'Txt files(*.txt)')
        file_path = QFileDialog.getSaveFileName(self, "保存mask", self.mask_path, "Txt files(*.txt)")
        root_path = os.path.dirname(file_path[0])
        file_name = file_path[0].split('/')[-1]
        envelope_mask_path = root_path + file_name.split('.')[0] + '$envelope.txt'
        envelope_img_path = root_path + file_name.split('.')[0] + '_envelope.jpg'
        outline_mask_path = root_path + file_name.split('.')[0] + '$outline.txt'
        self.im_seg.arr2txt(self.im_seg.envelop_array,envelope_mask_path)
        self.im_seg.array2img(self.im_seg.envelop_array,envelope_img_path)
        self.im_seg.gen_outline(envelope_img_path,outline_mask_path)


    def call_array(self):
        file_path = QFileDialog.getOpenFileName(self, '调用mask', self.mask_path, "Txt files(*.txt)")
        root_path = os.path.dirname(file_path[0])
        file_name = file_path[0].split('/')[-1]
        self.envelope_mask_path = root_path + file_name.split('$')[0] + '$envelope.txt'
        self.outline_mask_path = root_path + file_name.split('$')[0] + '$outline.txt'

    def clear_array(self):
        self

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

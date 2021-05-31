from .hktools import HKTools
import os
import requests
import cv2
import numpy as np
from queue import Queue
import datetime

class ImRecognition():
    def __init__(self,hktool:HKTools,root_path:str,ptz:bool,host = 'http://127.0.0.2:24401/'):
        self.hktool = hktool
        self.root_path = root_path
        self.ptz = ptz
        self.host = host
        self.display_q = Queue()
        self.color_tuple = tuple()

    def recognition(self):
        if self.ptz:
            while True:
                filepath = self.hktool.snapshot_ptz_q.get()
                # 建立存储处理完图像的文件夹
                folder_path = '{}\\{}'.format(self.root_path, filepath.split('\\')[-2])
                if not os.path.exists(folder_path):
                    print('mkdir {}'.format(folder_path))
                    os.mkdir(folder_path)
                # 图像文件路径定位
                new_filepath = '{}\\{}\\{}'.format(self.root_path, filepath.split('\\')[-2], filepath.split('\\')[-1])

                ori_img = cv2.imread(filepath).astype(np.float32)
                with open(filepath, 'rb') as f:
                    img = f.read()
                now = datetime.datetime.now()
                try:
                    results = requests.post(self.host, params={'threshold': 0.8}, data=img).json()['results']
                except Exception as e:
                    results = list()
                    with open('D:\\error.txt','a+') as f:
                        f.write('{}:{}\n'.format(datetime.datetime.now(),e))
                print('耗时：{}'.format(datetime.datetime.now() - now))
                try:
                    if results:
                        for item in results:
                            # Draw bbox
                            x1 = int(item["location"]["left"])
                            y1 = int(item["location"]["top"])
                            w = int(item["location"]["width"])
                            h = int(item["location"]["height"])
                            x2 = x1 + w
                            y2 = y1 + h
                            if item["name"] == 'torque_OK':
                                self.color_tuple = (0, 255, 0)
                            else:
                                self.color_tuple = (0, 0, 255)
                            if float(item["score"]) > 0.8:
                                cv2.rectangle(ori_img, (x1, y1), (x2, y2), self.color_tuple, 2)
                                cv2.putText(ori_img, "{} score: {}".format(item["name"], round(float(item["score"]), 4)),
                                            (x1, y1 - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (255, 255, 255), 1)
                        ori_img = ori_img.astype(np.uint8)

                    cv2.imwrite(new_filepath, ori_img)
                    self.display_q.put(new_filepath)
                except Exception as e:
                    with open('D:\\error.txt','a+') as f:
                        f.write('{}:{}\n'.format(datetime.datetime.now(),e))
        else:
            while True:
                filepath = self.hktool.snapshot_normal_q.get()
                # 建立存储处理完图像的文件夹
                folder_path = '{}\\{}'.format(self.root_path, filepath.split('\\')[-2])
                if not os.path.exists(folder_path):
                    print('mkdir {}'.format(folder_path))
                    os.mkdir(folder_path)
                # 图像文件路径定位
                new_filepath = '{}\\{}\\{}'.format(self.root_path, filepath.split('\\')[-2], filepath.split('\\')[-1])
                # TODO:目前先放原始照片，待算法完善后放处理后照片
                ori_img = cv2.imread(filepath).astype(np.float32)
                with open(filepath, 'rb') as f:
                    img = f.read()
                now = datetime.datetime.now()
                try:
                    results = requests.post(self.host, params={'threshold': 0.8}, data=img).json()[
                        'results']
                except Exception as e:
                    results = list()
                    with open('D:\\error.txt','a+') as f:
                        f.write('{}:{}\n'.format(datetime.datetime.now(),e))
                print('耗时：{}'.format(datetime.datetime.now() - now))
                try:
                    if results:
                        for item in results:
                            # Draw bbox
                            x1 = int(item["location"]["left"])
                            y1 = int(item["location"]["top"])
                            w = int(item["location"]["width"])
                            h = int(item["location"]["height"])
                            x2 = x1 + w
                            y2 = y1 + h
                            if item["name"] == 'torque_OK':
                                self.color_tuple = (0, 255, 0)
                            else:
                                self.color_tuple = (0, 0, 255)
                            if float(item["score"])>0.8:
                                cv2.rectangle(ori_img, (x1, y1), (x2, y2), self.color_tuple, 2)
                                cv2.putText(ori_img, "{} score: {}".format(item["name"], round(float(item["score"]), 4)),
                                            (x1, y1 - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (255, 255, 255), 1)
                        ori_img = ori_img.astype(np.uint8)

                    cv2.imwrite(new_filepath, ori_img)
                    self.display_q.put(new_filepath)
                except Exception as e:
                    with open('D:\\error.txt','a+') as f:
                        f.write('{}:{}\n'.format(datetime.datetime.now(),e))

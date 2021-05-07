from .hktools import HKTools
import os
import requests
import cv2
import numpy as np
from queue import Queue
import datetime

class ImRecognition():
    def __init__(self,hktool:HKTools,root_path:str,ptz:bool):
        self.hktool = hktool
        self.root_path = root_path
        self.ptz = ptz
        self.display_q = Queue()

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
                height, width = ori_img.shape[:2]
                with open(filepath, 'rb') as f:
                    img = f.read()
                now = datetime.datetime.now()
                try:
                    results = requests.post('http://127.0.0.2:24401/', params={'threshold': 0.8}, data=img).json()['results']
                except Exception as e:
                    results = list()
                    print('error occured:{}'.format(e))
                print('耗时：{}'.format(datetime.datetime.now() - now))
                if results:
                    for item in results:
                        # Draw bbox
                        x1 = int(item["location"]["left"])
                        y1 = int(item["location"]["top"])
                        w = int(item["location"]["width"])
                        h = int(item["location"]["height"])
                        x2 = x1 + w
                        y2 = y1 + h

                        cv2.rectangle(ori_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(ori_img, "{} score: {}".format(item["name"], round(float(item["score"]), 4)),
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (255, 255, 255), 1)
                    ori_img = ori_img.astype(np.uint8)
                    cv2.imwrite(new_filepath, ori_img)

                    self.display_q.put(new_filepath)
                else:
                    self.display_q.put(filepath)
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
                height, width = ori_img.shape[:2]
                with open(filepath, 'rb') as f:
                    img = f.read()
                now = datetime.datetime.now()
                try:
                    results = requests.post('http://127.0.0.2:24401/', params={'threshold': 0.8}, data=img).json()[
                        'results']
                except Exception as e:
                    results = list()
                    print('error occured:{}'.format(e))
                print('耗时：{}'.format(datetime.datetime.now() - now))
                if results:
                    for item in results:
                        # Draw bbox
                        x1 = int(item["location"]["left"])
                        y1 = int(item["location"]["top"])
                        w = int(item["location"]["width"])
                        h = int(item["location"]["height"])
                        x2 = x1 + w
                        y2 = y1 + h

                        cv2.rectangle(ori_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(ori_img, "{} score: {}".format(item["name"], round(float(item["score"]), 4)),
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (255, 255, 255), 1)
                    ori_img = ori_img.astype(np.uint8)
                    cv2.imwrite(new_filepath, ori_img)

                    self.display_q.put(new_filepath)
                else:
                    self.display_q.put(filepath)

from .hktools import HKTools
import os
import requests
import pycocotools.mask as mask_util
import cv2
import numpy as np
from queue import Queue
import datetime

# 处理图片，判断整车姿态是否有问题
class ImSeg():
    def __init__(self,hktool:HKTools,root_path:str):
        self.hktool = hktool
        # 每3600张图删除一次
        self.del_file = []
        self.del_file_new = []
        self.root_path = root_path
        # 需要显示的图片统一处理
        self.display_q = Queue()

    def segmentation(self):
        i = 0
        while True:
            filepath = self.hktool.snapshot_normal_q.get()
            # 建立存储处理完图像的文件夹
            folder_path = '{}\\{}'.format(self.root_path, filepath.split('\\')[-2])
            if not os.path.exists(folder_path):
                print('mkdir {}'.format(folder_path))
                os.mkdir(folder_path)
            # 图像文件路径定位
            new_filepath = '{}\\{}\\{}'.format(self.root_path,filepath.split('\\')[-2],filepath.split('\\')[-1])

            ori_img = cv2.imread(filepath).astype(np.float32)
            height, width = ori_img.shape[:2]

            with open(filepath,'rb') as f:
                img = f.read()

            # TODO:实在太TM慢了，平均45秒！
            now = datetime.datetime.now()
            try:
                result = requests.post('http://127.0.0.1:24401/', params={'threshold': 0.1},data=img).json()['results']
            except Exception as e:
                result = list()
                print('error occured:{}'.format(e))
            print('耗时：{}'.format(datetime.datetime.now() - now))
            # 有结果，能识别出来
            if result:
                # 轮廓识别标签只有一个
                img = result[0]['mask']
                rle_obj = {"counts": img, "size": [height, width]}
                mask = mask_util.decode(rle_obj)

                # TODO：需要确认是否需要再encode
                new_rle_obj = mask_util.encode(mask)
                # TODO：需要定义一个确定的颜色
                random_color = np.array([np.random.random() * 255.0, np.random.random() * 255.0, np.random.random() * 255.0])

                idx = np.nonzero(mask)
                alpha = 0.5
                ori_img[idx[0], idx[1], :] *= 1.0 - alpha
                ori_img[idx[0], idx[1], :] += alpha * random_color

                ori_img = ori_img.astype(np.uint8)
                cv2.imwrite(new_filepath,ori_img)

                self.del_file.append(filepath)
                self.del_file_new.append(new_filepath)
                self.display_q.put(new_filepath)

                i += 1
                if not i % 3600:
                    for j in range(0,3600):
                        if os.path.exists(self.del_file[j]):
                            os.remove(self.del_file[j])
                        if os.path.exists(self.del_file_new[j]):
                            os.remove(self.del_file_new[j])
                    self.del_file.clear()
                    self.del_file_new.clear()
                    i = 0
            # 无结果，无法识别出驾驶室
            else:
                # TODO：是否直接采取措施关停？
                print('no result')

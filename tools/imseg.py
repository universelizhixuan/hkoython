from .hktools import HKTools
import os
import requests
import pycocotools.mask as mask_util
import cv2
import numpy as np
from queue import Queue
import datetime
from threading import Event

# 处理图片，判断整车姿态是否有问题
class ImSeg():
    def __init__(self,hktool:HKTools,root_path:str,resolution:tuple=(1440,2560)):
        self.hktool = hktool
        self.resolution = resolution
        self.root_path = root_path
        # 需要显示的图片统一处理，直接传输图片信息，只有出现错误再保存
        self.display_q = Queue()
        # 错误图片路径存储
        self.errorpath_q = Queue()
        # 包络数组
        self.envelop_array = np.zeros(self.resolution,dtype='uint8',order='F')
        # 是否在包络内
        self.flag = True


    #完成图像分割，生成mask
    def gen_mask(self,filepath):
        ori_img = cv2.imread(filepath).astype(np.float32)
        height, width = ori_img.shape[:2]

        with open(filepath, 'rb') as f:
            img = f.read()

        # TODO:实在太TM慢了，平均45秒！
        now = datetime.datetime.now()
        try:
            result = requests.post('http://127.0.0.1:24401/', params={'threshold': 0.1}, data=img).json()['results']
        except Exception as e:
            result = list()
            with open('D:\\error.txt', 'a+') as f:
                f.write('{}:{}\n'.format(datetime.datetime.now(), e))
        print('耗时：{}'.format(datetime.datetime.now() - now))
        # 有结果，能识别出来
        if result:
            try:
                # 轮廓识别标签只有一个
                img = result[0]['mask']
                rle_obj = {"counts": img, "size": [height, width]}
                mask = mask_util.decode(rle_obj)
                return mask
            except Exception as e:
                with open('D:\\error.txt', 'a+') as f:
                    f.write('{}:{}\n'.format(datetime.datetime.now(), e))
                return 'error'
        # 无结果，无法识别出驾驶室
        else:
            return 'no result'

    # array到txt，工具函数。array：mask数组，path：txt存储路径
    def arr2txt(self,array,path):
        with open(path, 'w') as f:
            f.write(mask_util.encode(array)['counts'].decode('utf-8'))
    # txt到array转换，工具函数。path：txt存储路径
    # TODO:梁兴杰
    def txt2array(self,path):
        with open(path,'r') as f:
            img = f.read()
        rle_obj = {"counts": img, "size": list(self.resolution)}
        return mask_util.decode(rle_obj)


    # 生成轮廓函数。envelope_event由GUI传入，如isSet为True，开始采集并计算包络；如isSet为False，结束采集包络。默认为False
    # TODO:GUI形式需要确定，核心要求两个标志互斥，且有保存界面。在GUI类里完成mask文件存储及调用
    def gen_envelope(self,envelope_event:Event):
        while True:
            if envelope_event:
                filepath = self.hktool.snapshot_normal_q.get()
                mask = self.gen_mask(filepath)
                os.remove(filepath)

                if mask == 'error':
                    # TODO:处理
                    pass
                elif mask == 'no result':
                    # TODO:处理
                    pass
                # 生成包络
                else:
                    self.envelop_array = self.envelop_array | mask
            else:
                break

    # 生成轮廓线，工具函数
    def gen_outline(self,envelope_img_path,outline_array_path):
        img = cv2.imread(envelope_img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 1, 1)  # 核尺寸通过对图像的调节自行定义
        ret, thresh1 = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)  # 二进制阈值化
        x = cv2.Scharr(thresh1, cv2.CV_32F, 1, 0)  # X方向
        y = cv2.Scharr(thresh1, cv2.CV_32F, 0, 1)  # Y方向
        absX = cv2.convertScaleAbs(x)
        absY = cv2.convertScaleAbs(y)
        scharr = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
        scharr = np.asarray(scharr, dtype='uint8', order='F')
        scharr[scharr != 0] = 1
        outline_mask = mask_util.encode(scharr)['counts'].decode('utf-8')
        with open(outline_array_path, 'w') as f:
            f.write(outline_mask)

    # 功能：(1)队列取图片生成mask；(2)判断mask是否在包络内；(3)将判断结果生成当前mask+包络线的图片，直接放入display_q，作为显示用；(4)对于判断NG的，存储并将文件路径放入errorpath_q
    # filepath:envelop_array存储的txt文件,pixel_threshold为允许的像素差阈值
    def judge_mask(self,envelop_array_path,outline_array_path,pixel_threshold):
        envelop_array = self.txt2array(envelop_array_path)
        outline_array = self.txt2array(outline_array_path)

        while True:
            filepath = self.hktool.snapshot_normal_q.get()
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

            # TODO:实在太TM慢了，平均45秒！
            now = datetime.datetime.now()
            try:
                result = requests.post('http://127.0.0.1:24401/', params={'threshold': 0.1}, data=img).json()['results']
            except Exception as e:
                result = list()
                with open('D:\\error.txt', 'a+') as f:
                    f.write('{}:{}\n'.format(datetime.datetime.now(), e))
            print('耗时：{}'.format(datetime.datetime.now() - now))
            # 有结果，能识别出来
            if result:
                try:
                    # 轮廓识别标签只有一个
                    img = result[0]['mask']
                    rle_obj = {"counts": img, "size": [height, width]}
                    mask = mask_util.decode(rle_obj)
                    # 比较从文件读取包络和当前mask的区别
                    array = np.subtract(envelop_array, mask)
                    if len(array[array == 255]) > pixel_threshold:
                        self.flag = False
                    else:
                        self.flag = True
                    # 轮廓线和图片的mask合并
                    array_add = np.add(outline_array,mask)
                    # TODO：需要定义一个确定的颜色
                    random_color = np.array(
                        [np.random.random() * 255.0, np.random.random() * 255.0, np.random.random() * 255.0])

                    idx = np.nonzero(array_add)
                    alpha = 0.5
                    ori_img[idx[0], idx[1], :] *= 1.0 - alpha
                    ori_img[idx[0], idx[1], :] += alpha * random_color

                    ori_img = ori_img.astype(np.uint8)


                    self.display_q.put(new_filepath)
                    if self.flag:
                        cv2.putText(ori_img, "OK",(5, 5), cv2.FONT_HERSHEY_PLAIN, 14, (0, 255, 0), 3)
                        cv2.imwrite(new_filepath, ori_img)
                        os.remove(filepath)
                    else:
                        cv2.putText(ori_img, "NG",(5, 5), cv2.FONT_HERSHEY_PLAIN, 14, (0, 0, 255), 3)
                        cv2.imwrite(new_filepath, ori_img)
                        self.errorpath_q.put(new_filepath)
                except Exception as e:
                    with open('D:\\error.txt', 'a+') as f:
                        f.write('{}:{}\n'.format(datetime.datetime.now(), e))
            # 无结果，无法识别出驾驶室
            else:
                # TODO：是否直接采取措施关停？
                print('no result')

    # 初版，函数完整作为参考
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
                with open('D:\\error.txt','a+') as f:
                    f.write('{}:{}\n'.format(datetime.datetime.now(),e))
            print('耗时：{}'.format(datetime.datetime.now() - now))
            # 有结果，能识别出来
            if result:
                try:
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
                except Exception as e:
                    with open('D:\\error.txt','a+') as f:
                        f.write('{}:{}\n'.format(datetime.datetime.now(),e))
            # 无结果，无法识别出驾驶室
            else:
                # TODO：是否直接采取措施关停？
                print('no result')

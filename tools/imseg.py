from .hktools import HKTools
import os
import requests
import pycocotools.mask as mask_util
import cv2
import numpy as np
from queue import Queue
import datetime
from threading import Event
from PIL import Image

# 处理图片，判断整车姿态是否有问题
class ImSeg():
    def __init__(self,hktool:HKTools,root_path:str,resolution:tuple=(1440,2560),host = 'http://127.0.0.1:24401/'):
        self.hktool = hktool
        self.resolution = resolution
        self.host = host
        self.root_path = root_path
        # 需要显示的图片统一处理，直接传输图片信息，只有出现错误再保存
        self.display_q = Queue()
        # 错误图片路径存储
        self.errorpath_q = Queue()
        # 包络数组
        self.envelop_array = np.zeros(self.resolution,dtype='uint8',order='F')
        # 是否开始采集轮廓
        self.envelope_event = Event()
        # 是否判断
        self.judge_event = Event()
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
            result = requests.post(self.host, params={'threshold': 0.1}, data=img).json()['results']
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
    def txt2array(self,path):
        with open(path,'r') as f:
            print(path)
            img = f.read()
        rle_obj = {"counts": img, "size": list(self.resolution)}
        return mask_util.decode(rle_obj)

    # array到图片转换，工具函数。path：img存储路径
    def array2img(self,array,path):
        im = Image.new('RGB', (self.resolution[1], self.resolution[0]), 'white')
        im.save('D:\\white.jpg')
        ori_img = cv2.imread('D:\\white.jpg').astype(np.float32)
        alpha = 1
        color = np.array([0, 0, 255])
        idx = np.nonzero(array)
        ori_img[idx[0], idx[1], :] *= 1.0 - alpha
        ori_img[idx[0], idx[1], :] += alpha * color
        ori_img = ori_img.astype(np.uint8)
        cv2.imwrite(path, ori_img)

    # 生成轮廓函数。self.envelope_event由GUI传入，如isSet为True，开始采集并计算包络；如isSet为False，结束采集包络。默认为False
    # TODO:GUI形式需要确定，核心要求两个标志互斥，且有保存界面。在GUI类里完成mask文件存储及调用
    def gen_envelope(self):
        while True:
            print(1)
            self.envelope_event.wait()
            print(2)
            filepath = self.hktool.snapshot_normal_q.get()
            mask = self.gen_mask(filepath)
            print(mask)
            # os.remove(filepath)

            if mask is 'error':
                # TODO:处理
                pass
            elif mask is 'no result':
                # TODO:处理
                pass
            # 生成包络
            else:
                self.envelop_array = self.envelop_array | mask

    # 生成轮廓线，工具函数
    # TODO:梁兴杰
    def gen_outline(self,envelope_mask_path,outline_array_path,n= 20):
        envelope_array = self.txt2array(envelope_mask_path)
        envelope_list = []
        h, w = envelope_array.shape
        new_envelope_array = np.zeros((h, w), dtype='uint8', order='F')
        Flag = False
        # 找第一个轮廓上的点，考虑的是第一行，最后一行，第一列，最后一列不存在1的情况
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if envelope_array[i][j] == 1:
                    envelope_list.append((i, j))
                    # print(i,j)
                    # print('-------')
                    Flag = True
                    break
            if Flag:
                break
        for x,y in envelope_list:
            for a in range(-1, 2):
                for b in range(-1, 2):
                    # print('a,b',a,b)
                    if envelope_array[x + a][y + b] == 1 and (x + a, y + b) not in envelope_list:
                        if envelope_array[x + a + 1][y + b] + envelope_array[x + a - 1][y + b] + envelope_array[x + a][y + b + 1] + envelope_array[x + a][y + b - 1] < 4:
                            envelope_list.append((x + a, y + b))
        # 修改轮廓数组，并加粗线条
        for x, y in envelope_list:
            for a in range(-n, n + 1):
                for b in range(-n, n + 1):
                    new_envelope_array[x + a][y + b] = 1
        new_envelope_array = new_envelope_array & envelope_array
        outline_mask = mask_util.encode(new_envelope_array)['counts'].decode('utf-8')
        with open(outline_array_path, 'w') as f:
            f.write(outline_mask)

    # 功能：(1)队列取图片生成mask；(2)判断mask是否在包络内；(3)将判断结果生成当前mask+包络线的图片，直接放入display_q，作为显示用；(4)对于判断NG的，存储并将文件路径放入errorpath_q
    # filepath:envelop_array存储的txt文件,pixel_threshold为允许的像素差阈值
    def judge_mask(self,envelop_array_path,outline_array_path,pixel_threshold):
        envelop_array = self.txt2array(envelop_array_path)
        outline_array = self.txt2array(outline_array_path)
        '''驾驶室的运动包络和驾驶室某时刻的轮廓颜色不同，两者需分别定义颜色，颜色是按照BGR模式定义。如果不是BGR模式，需要修改数值。
            驾驶室正常姿态运动边界颜色为绿色。某时刻驾驶室姿态正常，运动的轮廓是蓝色；当某时刻驾驶室轮廓出界时，该时刻驾驶室轮廓为红色。'''
        # 定义驾驶室正常姿态运动包络的轮廓
        idx_normal = np.nonzero(outline_array)
        # 驾驶室正常姿态的轮廓是蓝色
        outline_normal_color = [255, 0, 0]
        while True:
            if self.judge_event.isSet():
                filepath = self.hktool.snapshot_normal_q.get()
                # 建立存储处理完图像的文件夹
                folder_path = '{}\\{}'.format(self.root_path, filepath.split('\\')[-2])
                if not os.path.exists(folder_path):
                    print('mkdir {}'.format(folder_path))
                    os.mkdir(folder_path)
                # 图像文件路径定位
                new_filepath = '{}\\{}\\{}'.format(self.root_path, filepath.split('\\')[-2], filepath.split('\\')[-1])

                ori_img = cv2.imread(filepath).astype(np.float32)
                mask = self.gen_mask(filepath)
                idx = np.nonzero(mask)
                if mask is 'error':
                    # TODO:措施
                    pass
                elif mask is 'no result':
                    # TODO:措施
                    pass
                else:
                    # 比较从文件读取包络和当前mask的区别
                    array = np.subtract(envelop_array, mask)
                    if len(array[array == 255]) > pixel_threshold:
                        self.flag = False
                    else:
                        self.flag = True
                    # # 轮廓线和图片的mask合并
                    # array_add = np.add(outline_array,mask)
                    # # TODO：需要定义一个确定的颜色
                    # random_color = np.array(
                    #     [np.random.random() * 255.0, np.random.random() * 255.0, np.random.random() * 255.0])
                    #
                    # idx = np.nonzero(array_add)
                    # alpha = 0.5
                    # ori_img[idx[0], idx[1], :] *= 1.0 - alpha
                    # ori_img[idx[0], idx[1], :] += alpha * random_color
                    #
                    # ori_img = ori_img.astype(np.uint8)
                    # if self.flag:
                    #     # cv2.putText(ori_img, "OK",(5, 5), cv2.FONT_HERSHEY_PLAIN, 14, (0, 255, 0), 3)
                    #     cv2.imwrite(new_filepath, ori_img)
                    #     print('OK')
                    #     # os.remove(filepath)
                    # else:
                    #     # cv2.putText(ori_img, "NG",(5, 5), cv2.FONT_HERSHEY_PLAIN, 14, (0, 0, 255), 3)
                    #     cv2.imwrite(new_filepath, ori_img)
                    #     self.errorpath_q.put(new_filepath)
                    #     print('NG')
                    # print(new_filepath)
                    # self.display_q.put(new_filepath)
                    alpha = 0.5
                    if self.flag:
                        # BGR模式下是绿色，其他颜色模式需调整
                        outline_color = [0, 255, 0]
                        ori_img[idx[0], idx[1], :] *= alpha
                        ori_img[idx[0], idx[1], :] += (1 - alpha) * outline_color
                        ori_img[idx_normal[0], idx_normal[1], :] = outline_normal_color
                        ori_img = ori_img.astype(np.uint8)

                        cv2.putText(ori_img, "OK", (5, 5), cv2.FONT_HERSHEY_PLAIN, 14, (0, 255, 0), 3)
                        cv2.imwrite(new_filepath, ori_img)
                        self.display_q.put(new_filepath)
                    else:
                        # BGR模式下是红色，其他颜色模式需调整
                        outline_color = [0, 0, 255]
                        ori_img[idx[0], idx[1], :] *= alpha
                        ori_img[idx[0], idx[1], :] += (1 - alpha) * outline_color
                        ori_img[idx_normal[0], idx_normal[1], :] = outline_normal_color
                        ori_img = ori_img.astype(np.uint8)
                        cv2.putText(ori_img, "NG", (5, 5), cv2.FONT_HERSHEY_PLAIN, 14, (0, 0, 255), 3)
                        cv2.imwrite(new_filepath, ori_img)
                        self.display_q.put(new_filepath)
                        self.errorpath_q.put(new_filepath)

            else:
                break

    # 初版，函数完整作为参考
    # def segmentation(self):
    #     i = 0
    #     while True:
    #         filepath = self.hktool.snapshot_normal_q.get()
    #         # 建立存储处理完图像的文件夹
    #         folder_path = '{}\\{}'.format(self.root_path, filepath.split('\\')[-2])
    #         if not os.path.exists(folder_path):
    #             print('mkdir {}'.format(folder_path))
    #             os.mkdir(folder_path)
    #         # 图像文件路径定位
    #         new_filepath = '{}\\{}\\{}'.format(self.root_path,filepath.split('\\')[-2],filepath.split('\\')[-1])
    #
    #         ori_img = cv2.imread(filepath).astype(np.float32)
    #         height, width = ori_img.shape[:2]
    #
    #         with open(filepath,'rb') as f:
    #             img = f.read()
    #
    #         # TODO:实在太TM慢了，平均45秒！
    #         now = datetime.datetime.now()
    #         try:
    #             result = requests.post(self.host, params={'threshold': 0.1},data=img).json()['results']
    #         except Exception as e:
    #             result = list()
    #             with open('D:\\error.txt','a+') as f:
    #                 f.write('{}:{}\n'.format(datetime.datetime.now(),e))
    #         print('耗时：{}'.format(datetime.datetime.now() - now))
    #         # 有结果，能识别出来
    #         if result:
    #             try:
    #                 # 轮廓识别标签只有一个
    #                 img = result[0]['mask']
    #                 rle_obj = {"counts": img, "size": [height, width]}
    #                 mask = mask_util.decode(rle_obj)
    #                 new_rle_obj = mask_util.encode(mask)
    #                 random_color = np.array([np.random.random() * 255.0, np.random.random() * 255.0, np.random.random() * 255.0])
    #
    #                 idx = np.nonzero(mask)
    #                 alpha = 0.5
    #                 ori_img[idx[0], idx[1], :] *= 1.0 - alpha
    #                 ori_img[idx[0], idx[1], :] += alpha * random_color
    #
    #                 ori_img = ori_img.astype(np.uint8)
    #                 cv2.imwrite(new_filepath,ori_img)
    #
    #                 self.del_file.append(filepath)
    #                 self.del_file_new.append(new_filepath)
    #                 self.display_q.put(new_filepath)
    #
    #                 i += 1
    #                 if not i % 3600:
    #                     for j in range(0,3600):
    #                         if os.path.exists(self.del_file[j]):
    #                             os.remove(self.del_file[j])
    #                         if os.path.exists(self.del_file_new[j]):
    #                             os.remove(self.del_file_new[j])
    #                     self.del_file.clear()
    #                     self.del_file_new.clear()
    #                     i = 0
    #             except Exception as e:
    #                 with open('D:\\error.txt','a+') as f:
    #                     f.write('{}:{}\n'.format(datetime.datetime.now(),e))
    #         # 无结果，无法识别出驾驶室
    #         else:
    #             print('no result')

from threading import Thread
from tools.hktools import HKTools
from tools.imseg import ImSeg
from tools.imrecognition import ImRecognition
from tools.mainwindow import gen_mainwindow

# 后部固定摄像头：监控整车姿态及提供运动状态,输出照片
hktool_normal_1 = HKTools('192.168.1.63', 'admin', 'dflli88!')
# PTZ摄像头1#
hktool_ptz_1 = HKTools('192.168.1.178', 'admin', 'Syc2018!')
# PTZ摄像头2#
hktool_ptz_2 = HKTools('192.168.1.62', 'admin', 'dflli88!')

# 识别驾驶室姿态实例。接受hktool的照片，经过处理，生成处理后的照片
im_seg = ImSeg(hktool_normal_1, 'D:\\MTS\\normal-1-handle')
imrec_ptz_1 = ImRecognition(hktool_ptz_1, 'D:\\MTS\\ptz-1-handle', ptz=True)
imrec_ptz_2 = ImRecognition(hktool_ptz_2, 'D:\\MTS\\ptz-2-handle', ptz=True)

# 可视化塞照片进mixed_q_dict
mixed_q_dict = {'normal-1':im_seg.display_q,'ptz-1':imrec_ptz_1.display_q,'ptz-2':imrec_ptz_2.display_q}

# 生成{时间戳:0/1}
t1 = Thread(target=hktool_normal_1.deploy)
t2 = Thread(target=hktool_normal_1.genlist)
t3 = Thread(target=hktool_normal_1.gendict)
t4 = Thread(target=hktool_normal_1.snapshot_normal, args = ('D:\\MTS\\normal-1',True,2.5,))
# PTZ摄像头1#截屏
t5 = Thread(target=hktool_ptz_1.snapshot_ptz, args=((4, 0), (1, 31), 'D:\\MTS\\ptz-1',))
# PTZ摄像头2#截屏
t6 = Thread(target=hktool_ptz_2.snapshot_ptz, args=((4, 0), (1, 31), 'D:\\MTS\\ptz-2',))

# 识别驾驶室姿态
t7 = Thread(target=im_seg.gen_envelope)
t8 = Thread(target=imrec_ptz_1.recognition)
t9 = Thread(target=imrec_ptz_2.recognition)

# 产生可视化窗口
t10 = Thread(target=gen_mainwindow,args=(mixed_q_dict,im_seg,'D:\\MTS\\mask'))


t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t7.start()
t8.start()
t9.start()
t10.start()
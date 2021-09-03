from ctypes import *
from data import NET_DVR_Login_V40
from data import NET_DVR_JPEGPARA
from data import MSesGCallback
from data import ALARM
import time
import datetime
from queue import Queue
import os
from threading import Event

alarmq = Queue(maxsize=0)
event_move = Event()
# 截图是否激活
flag = True


class HKTools:
    def __init__(self, url, username, password, port=8000, dll_path=r'D:\CH-HCNetSDKV6.1.6.4_build20201231_win64\dll'):
        self.url = url
        self.username = username
        self.password = password
        self.port = port
        self.dll_path = dll_path
        self.hksdk = self.load_dll()
        self.init_hksdk(self.hksdk)
        self.userid = self.login(self.hksdk)
        self.snapshot_ptz_q = Queue(maxsize=0)
        self.snapshot_normal_q = Queue(maxsize=0)
        self.alarm_set = set()
        self.handle = -1
        self.event_deploy = Event()

    def load_dll(self):
        # windll和cdll区别：windll导入的库按stdcall调用协议调用其中的函数，cdll载入按标准的cdecl调用协议导出的函数
        # 载入HCCore.dll
        hcnetsdk = cdll.LoadLibrary(self.dll_path + "\\HCNetSDK.dll")
        return hcnetsdk

    def init_hksdk(self, hksdk):
        if not hksdk.NET_DVR_Init():
            print("初始失败")
            return False
        if not hksdk.NET_DVR_SetConnectTime():
            print("设置连接时间失败")
            return False
        print("初始化成功")

    # 登陆函数，实例构造的时候自动调用
    def login(self, hksdk):
        # 通过ctypes中的bytes函数将python的str类型转化为C++的string类型(*char)
        burl = bytes(self.url, "ascii")
        busename = bytes(self.username, "ascii")
        bpassword = bytes(self.password, "ascii")

        login_info = NET_DVR_Login_V40.NET_DVR_USER_LOGIN_INFO()
        device_info = NET_DVR_Login_V40.NET_DVR_DEVICEINFO_V40()

        # 赋值login_info信息，一般device_info不用赋值
        login_info.wPort = self.port
        login_info.bUseAsynLogin = 0
        login_info.sUserName = busename
        login_info.sPassword = bpassword
        login_info.sDeviceAddress = burl

        # 通过ctypes中的byref将变量转换为C++中的指针
        param_login = byref(login_info)
        param_device = byref(device_info)

        # 调用登陆函数
        userid = hksdk.NET_DVR_Login_V40(param_login, param_device)
        if userid == -1:
            print("登录失败，错误码为{}".format(hksdk.NET_DVR_GetLastError()))
        else:
            print("登录成功，用户id为{}".format(userid))

        return userid

    # 登出函数，不自动调用
    def uinit(self, hksdk, userid):
        isOK = hksdk.NET_DVR_Logout(userid)
        if isOK == -1:
            print("登出失败错误码为{}".format(hksdk.NET_DVR_GetLastError()))
        else:
            print("登出成功")
        hksdk.NET_DVR_Cleanup()

    # 固定摄像头的截图函数
    # 存在两种用法：(1)识别轮廓，需实时识别；(2)识别螺栓，必须等台架停止运转后识别，通过event传入信号
    # 当contour(轮廓识别)为True时，采用轮廓识别，intervaltime时间即是采集间隔时间；当为False时，直接通过event传入信号
    def snapshot_normal(self, rootpath, contour=True, intervaltime=1):
        picpara = NET_DVR_JPEGPARA.NET_DVR_JPEGPARA()
        picpara.wPicSize = 9
        picpara.wPicQuality = 0
        if contour:
            time.sleep(5)
            while True:
                time.sleep(intervaltime)
                if not event_move.isSet():
                    nowtime = datetime.datetime.now()
                    folder_path = '{}\\{}'.format(rootpath, nowtime.strftime('%Y-%m-%d'))
                    if not os.path.exists(folder_path):
                        print('mkdir {}'.format(folder_path))
                        os.mkdir(folder_path)
                    filepath = '{}\\{}.jpg'.format(folder_path, nowtime.strftime('%H-%M-%S'))
                    errorcode = self.hksdk.NET_DVR_CaptureJPEGPicture(self.userid, 1, byref(picpara),
                                                                      bytes(filepath, "ascii"))
                    if not errorcode:
                        print('截图失败，时间{} {}'.format(nowtime.strftime('%Y-%m-%d'), nowtime.strftime('%H:%M:%S')))
                    else:
                        self.snapshot_normal_q.put(filepath)
        else:
            time.sleep(5)
            while True:
                if flag:
                    # 刚开的时候不截图
                    event_move.wait()
                    nowtime = datetime.datetime.now()
                    folder_path = '{}\\{}'.format(rootpath, nowtime.strftime('%Y-%m-%d'))
                    if not os.path.exists(folder_path):
                        print('mkdir {}'.format(folder_path))
                        os.mkdir(folder_path)
                    filepath = '{}\\{}.jpg'.format(folder_path, nowtime.strftime('%H-%M-%S'))
                    errorcode = self.hksdk.NET_DVR_CaptureJPEGPicture(self.userid, 1, byref(picpara),
                                                                      bytes(filepath, "ascii"))
                    if not errorcode:
                        print('截图失败，时间{} {}'.format(nowtime.strftime('%Y-%m-%d'), nowtime.strftime('%H:%M:%S')))
                    else:
                        self.snapshot_normal_q.put(filepath)

    # 球机的截图函数
    # 截图函数:interval = (leadtime,posttime),preset = (firstpreset,lastpreset)
    # 通过在rootpath下创建当前日期的文件夹，存储图片。日期命名格式"年-月-日"，图片命名格式"时-分-秒_预置点.jpg"
    def snapshot_ptz(self, intervaltime, preset, rootpath):
        picpara = NET_DVR_JPEGPARA.NET_DVR_JPEGPARA()
        picpara.wPicSize = 9
        picpara.wPicQuality = 0
        while True:
            if flag:
                # 刚开的时候不截图
                time.sleep(5)
                event_move.wait()
                for i in range(preset[0], preset[1]):
                    self.hksdk.NET_DVR_PTZPreset_Other(self.userid, 1, 39, i)
                    time.sleep(intervaltime[0])
                    nowtime = datetime.datetime.now()
                    folder_path = '{}\\{}'.format(rootpath, nowtime.strftime('%Y-%m-%d'))
                    if not os.path.exists(folder_path):
                        print('mkdir {}'.format(folder_path))
                        os.mkdir(folder_path)
                    filepath = '{}\\{}_{}.jpg'.format(folder_path, nowtime.strftime('%H-%M-%S'), i)
                    errorcode = self.hksdk.NET_DVR_CaptureJPEGPicture(self.userid, 1, byref(picpara),
                                                                      bytes(filepath, "ascii"))
                    if not errorcode:
                        print(
                            '截取预置点{}时失败，时间{} {}'.format(i, nowtime.strftime('%Y-%m-%d'), nowtime.strftime('%H:%M:%S')))
                    else:
                        self.snapshot_ptz_q.put(filepath)
                    time.sleep(intervaltime[1])

    @staticmethod
    @CFUNCTYPE(c_int, c_long, MSesGCallback.NET_DVR_ALARMER, c_char_p, c_ulong, c_void_p)
    def alarm_callback(lCommand: c_long, pAlarmer: MSesGCallback.NET_DVR_ALARMER, pAlarmInfo: c_char_p,
                       dwBufLen: c_ulong, pUser: c_void_p):
        # print("收到警报信息，类型为 {} \t发送者为 {}".format(lCommand, pAlarmer.lUserID))
        if lCommand == 0x4000:
            # NET_DVR_ALARMINFO_V30 alarmInfo;
            # memcpy(&alarmInfo, pAlarmInfo, sizeof(NET_DVR_ALARMINFO_V30));

            alarmq.put(datetime.datetime.now().timestamp())

            alarm_info = ALARM.NET_DVR_ALARMINFO_V30()
            memmove(addressof(alarm_info), pAlarmInfo.decode("ascii"), sizeof(alarm_info))
            if alarm_info.dwAlarmType == 3:
                pass
                # print("子事件为移动侦测")
            else:
                print("子事件 None")
        else:
            print("消息类型为None")

        return 1

    def deploy(self):  # 布防
        # 设置回调函数
        callback_status = self.hksdk.NET_DVR_SetDVRMessageCallBack_V31(self.alarm_callback, None)
        if callback_status == -1:
            print("设置回调函数失败，错误码为".format(self.hksdk.NET_DVR_GetLastError()))
            return -1
        else:
            print("设置回调函数成功")

        # 启用布防
        setup_alarm = ALARM.NET_DVR_SETUPALARM_PARAM()
        setup_alarm.dwSevel = 0
        setup_alarm.byAize = sizeof(ALARM.NET_DVR_SETUPALARM_PARAM)
        setup_alarm.byLlarmInfoType = 1
        self.handle = self.hksdk.NET_DVR_SetupAlarmChan_V41(self.userid, setup_alarm)
        if self.handle < 0:
            print("布防失败，错误码为{}".format(self.hksdk.NET_DVR_GetLastError()))

        else:
            print("布防成功")
            print("***************警告信息输出begin******************")
            self.event_deploy.wait()
            print("****************警告信息输出end*******************")
            print("开始撤防。。。")
            self.disdeploy()

    def genlist(self):
        while True:
            timestampnow = int(alarmq.get())
            # print(timestampnow)
            for i in range(0, 14):
                if timestampnow + i not in self.alarm_set:
                    self.alarm_set.add(timestampnow + i)

    def gendict(self):
        global flag
        nowstamp = int(datetime.datetime.now().timestamp()) - 3
        while True:
            if nowstamp in self.alarm_set:
                flag = True
                print('{}:{}'.format(datetime.datetime.fromtimestamp(nowstamp).strftime("%Y-%m-%d %H:%M:%S"), 1))
                if event_move.isSet():
                    event_move.clear()
            else:
                print('{}:{}'.format(datetime.datetime.fromtimestamp(nowstamp).strftime("%Y-%m-%d %H:%M:%S"), 0))
                flag = False
                if not event_move.isSet():
                    event_move.set()
            nowstamp += 1
            # 万一卡一下，时间变成负的会出现异常
            try:
                time.sleep(1.1 - (datetime.datetime.now().timestamp() - 2 - nowstamp))
            except:
                pass

    def disdeploy(self):  # 布防
        disdeploy_result = self.hksdk.NET_DVR_CloseAlarmChan_V30(self.handle)
        if disdeploy_result == -1:
            print("撤防失败，错误码为{}".format(self.hksdk.NET_DVR_GetLastError()))
        else:
            print("撤防成功")

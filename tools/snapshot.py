
from tools.hkAdapter import HkAdapter
from data import NET_DVR_Login_V40
from ctypes import *
from data import MSesGCallback
from data import ALARM
import time
from data import NET_DVR_JPEGPARA



def init(hksdk):
    if not hksdk.NET_DVR_Init():
        print("初始失败")
        return False
    if not hksdk.NET_DVR_SetConnectTime():
        print("设置连接时间失败")
        return False
    print("初始化成功")
    return True

# url = 192.168.1.64，username = admin,password = huawei123
def login(hksdk, url, usename, password, port=8000):
    burl = bytes(url, "ascii")
    busename = bytes(usename, "ascii")
    bpassword = bytes(password, "ascii")

    login_info = NET_DVR_Login_V40.NET_DVR_USER_LOGIN_INFO()
    device_info = NET_DVR_Login_V40.NET_DVR_DEVICEINFO_V40()

    login_info.wPort = port
    login_info.bUseAsynLogin = 0
    login_info.sUserName = busename
    login_info.sPassword = bpassword
    login_info.sDeviceAddress = burl



    param_login = byref(login_info)  # 传递的为指针则使用该种方式,通过ctypes导入
    param_device = byref(device_info)
    print("call login method")
    useid = hksdk.NET_DVR_Login_V40(param_login, param_device)
    print("after login method")
    if useid == -1:
        print("登录失败，错误码为{}".format(hksdk.NET_DVR_GetLastError()))
    else:
        print("登录成功，用户id为{}".format(useid))
    print("最大模拟通道数为")

    return useid


@CFUNCTYPE(c_int, c_long, MSesGCallback.NET_DVR_ALARMER, c_char_p, c_ulong, c_void_p)
def alarm_callback(lCommand:c_long, pAlarmer:MSesGCallback.NET_DVR_ALARMER,
                   pAlarmInfo:c_char_p, dwBufLen:c_ulong, pUser:c_void_p):
    print("收到警报信息，类型为 {} \t发送者为 {}".format(lCommand, pAlarmer.lUserID))
    if lCommand == 0x4000:
        #NET_DVR_ALARMINFO_V30 alarmInfo;
		#memcpy(&alarmInfo, pAlarmInfo, sizeof(NET_DVR_ALARMINFO_V30));

        print("消息类型为 COMM_ALARM_V30",end=" --> ")
        alarm_info = ALARM.NET_DVR_ALARMINFO_V30()
        memmove(addressof(alarm_info),pAlarmInfo.decode("ascii"),sizeof(alarm_info))
        if alarm_info.dwAlarmType == 3:
            print("子事件为移动侦测")
        else:
            print("子事件 None")
    else:
        print("消息类型为None")

    return 1


def deploy(hksdk, userid):  # 布防
    # 设置回调函数
    callback_status = hksdk.NET_DVR_SetDVRMessageCallBack_V31(alarm_callback,None)
    if callback_status == -1:
        print("设置回调函数失败，错误码为".format(hksdk.NET_DVR_GetLastError()))
        return -1
    else:
        print("设置回调函数成功")

    #启用布防
    setup_alarm = ALARM.NET_DVR_SETUPALARM_PARAM()
    setup_alarm.dwSize = sizeof(ALARM.NET_DVR_SETUPALARM_PARAM)
    setup_alarm.byLevel = 0
    setup_alarm.byAlarmInfoType = 1
    handle = hksdk.NET_DVR_SetupAlarmChan_V41(userid,setup_alarm)
    if handle < 0 :
        print("布防失败，错误码为{}".format(hksdk.NET_DVR_GetLastError()))

    else:
        print("布防成功")
    return handle

def disdeploy(hksdk, handle):  # 布防
    disdeploy_result = hksdk.NET_DVR_CloseAlarmChan_V30(handle)
    if disdeploy_result == -1:
        print("撤防失败，错误码为{}".format(hksdk.NET_DVR_GetLastError()))
    else:
        print("撤防成功")



def uinit(hksdk, useid):
    isOK = hksdk.NET_DVR_Logout(useid)
    if isOK == -1:
        print("登出失败错误码为{}".format(hksdk.NET_DVR_GetLastError()))
    else:
        print("登出成功")
    hksdk.NET_DVR_Cleanup()


if __name__ == "__main__":
    print("-----------初始化与登录---------")
    hkadapter = HkAdapter()
    # hksdk代表一个dll本身
    hksdk = hkadapter.load_hkdll()
    init(hksdk)
    userid = login(hksdk, "192.168.1.178", "admin", "Syc2018!")
    print("----------初始化与登录完成---------")
    picpara = NET_DVR_JPEGPARA.NET_DVR_JPEGPARA()
    picpara.wPicSize = 9
    picpara.wPicQuality = 0
    for i in range(1,31):
        load_path = 'D:\\test\{}.jpg'.format(i)
        a = hksdk.NET_DVR_CaptureJPEGPicture(userid, 1, byref(picpara), bytes(load_path, "ascii"))
        hksdk.NET_DVR_PTZPreset_Other(userid,1,39,i)
        time.sleep(4)
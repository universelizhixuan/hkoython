from ctypes import *
class NET_DVR_JPEGPARA(Structure):
    _fields_ = [
        ("wPicSize", c_uint16),
        ("wPicQuality", c_uint16),
    ]
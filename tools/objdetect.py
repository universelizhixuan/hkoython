from tools.hktools import HKTools

class ObjDectect():
    # ackmethod为1，从snapshot_ptz_q里取数据；ackmethod为0，从snapshot_normal_q里取数据
    def __init__(self,hktool:HKTools,ackmethod:int):
        self.hktool = hktool
        self.ackmethod = ackmethod

    def detection(self):
        if self.ackmethod:
            while True:
                filepath = self.hktool.snapshot_ptz_q.get()
                with open(filepath, 'rb') as f:
                    img = f.read()

                # todo:machine learning
                # params为get参数 data 为POST Body
                # result = requests.post('http://127.0.0.1:24401',params = {'threshold':0.1},data= img).json()
                # print(result)
        else:
            while True:
                filepath = self.hktool.snapshot_normal_q.get()
                with open(filepath, 'rb') as f:
                    img = f.read()

                # todo:machine learning
                # params为get参数 data 为POST Body
                # result = requests.post('http://127.0.0.1:24401',params = {'threshold':0.1},data= img).json()
                # print(result)
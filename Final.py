from __future__ import absolute_import
#自编函数库
from MatureFunction import position_judge,send_to_server,Delete_file,sendobstxt
from iot_device_sdk_python.sendmessage import IOTEETH_MQTT
#opencv库，用于驱动usb和图像处理
import cv2
#从配置库中引入路径配置文件
from  Final_config import Path
#引入华为云obs
from obs import ObsClient
from obs import CreateBucketHeader
import traceback
import threading
import sys
import os
##下面这些都是iotda的相关库)

from typing import List
import time
import logging
from iot_device_sdk_python.client.listener.property_listener import PropertyListener
from iot_device_sdk_python.client.request.service_property import ServiceProperty
from iot_device_sdk_python.client import iot_result
from iot_device_sdk_python.client.client_conf import ClientConf
from iot_device_sdk_python.client.connect_auth_info import ConnectAuthInfo
from iot_device_sdk_python.client.listener.command_listener \
import CommandListener
from iot_device_sdk_python.iot_device import IotDevice
from iot_device_sdk_python.client.request.command_response import CommandRsp
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(threadName)s - %(filename)s[%(funcName)s] - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

############################################################################################################################


class Position():
    def __init__(self):
        self.position = 0#初始化位置
        self.ifDelete = 0
        self.ifSend = 0
        

def take_photo(mypath,pos,IOTDA,Property):
   
    #print("拍摄线程启动")
    cap = cv2.VideoCapture(0)#初始化相机
    if not cap.isOpened():
        print("无法识别到相机")
        #Property.usb = 0
        #Property.sendproperty(IOTDA.device)#上传属性
        print("上传属性usb=0")
        exit(0)
    #Property.usb = 1
    #Property.sendproperty(IOTDA.device)#上传属性
    #print("摄像头正常，上传属性usb=1")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while int(pos.position) < 3: #一直到4的时候，才会退出循环，保证程序正常结束

        #判断位置
        preposition =pos.position#用preposition保存之前的position值
        pos.position = position_judge(preposition,cap,Property,IOTDA)##################################
        Property.position=pos.position
        #一旦识别失败，提示重新扫描
        if pos.position =='error':
            Property.ifcorrect=0
            Property.sendproperty(IOTDA.device)#上传是否扫描准确
            #print("上传属性ifcorrect=0")
            print("识别位置信息错误，重新识别")
            pos.position =preposition
            Property.position=pos.position
            Property.sendproperty(IOTDA.device)#上传属性开始扫描的位置
            ###在此处应当清空缓存文件#######################################################
            if (pos.ifDelete ==0):
                pos.ifDelete = 1
       
            pos.position = preposition
            continue
        #向云服务端传送，每次发送都是整个文件的发送
        else:
            Property.ifcorrect=1#识别结果正确
            Property.sendproperty(IOTDA.device)#上传属性开始扫描的位置
            #print("上传属性ifcorrect=1")
            if (pos.ifSend ==0):#如果
                pos.ifSend = 1
            else:
                print("等待上传")
                while(1):
               
                    if(pos.ifSend == 0):
                        print("本次上传结束")
                        break
                pos.ifSend = 1
    #print("line1 over$$$$$$$$$$$$$$$$$$$$$$$$")


def obs(mypath,pos,IOTDA,Property):
    #print("云存储线程启动")
    obsClient = ObsClient(
        access_key_id='ZGCNBIRERUNYFPZY1JEW',  # 刚刚下载csv文件里面的Access Key Id
        secret_access_key='OzM4hTiyFsOEMZiowqnoIvG2NRF8gUsAZhd4VemX',  # 刚刚下载csv文件里面的Secret Access Key
        server='https://obs.cn-north-4.myhuaweicloud.com'# 这里的访问域名就是我们在桶的基本信息那里记下的东西
    )
    #使用访问OBS
    #调用putFile接口上传对象到桶内
    try:
        bucketName = 'ioteeth'
        resp = obsClient.headBucket(bucketName)
        if resp.status < 300:
            print('成功连接obs存储')
            Property.obs = 1
            #Property.sendproperty(IOTDA.device)#上传属性
            
        elif resp.status == 404:
            print('桶不存在')
            try:
                # 创建桶的附加头域，桶的访问控制策略是私有桶，存储类型是低频访问存储，多AZ方式存储
                header = CreateBucketHeader(aclControl="PRIVATE", storageClass="STANDARD", availableZone="3az")
                # 指定存储桶所在区域，此处以“ap-southeast-1”为例，必须跟传入的Endpoint中Region保持一致。
                location = "cn-north-4"
                bucketName = "ioteeth"
                # 创建桶
                resp = obsClient.createBucket(bucketName, header, location)
                # 返回码为2xx时，接口调用成功，否则接口调用失败
                if resp.status < 300:
                    print('创建桶成功')
                else:
                    print('创建桶失败')
                    #Property.obs = 0
                    #Property.sendproperty(IOTDA.device)#上传属性
                    print('requestId:', resp.requestId)
                    print('errorCode:', resp.errorCode)
                    print('errorMessage:', resp.errorMessage)
                    exit(0)
            except:
                print('创建桶失败')
                #Property.obs = 1
                #Property.sendproperty(IOTDA.device)#上传属性
                print(traceback.format_exc())
                exit(0)
    except:
        print('Head Bucket Failed')
        #Property.obs = 1
        #Property.sendproperty(IOTDA.device)#上传属性
        print(traceback.format_exc())
        exit(0)
    ind=0
    while(1):
        if(pos.ifDelete ==1):
            Delete_file(mypath, str(int(pos.position)+1))#############################################
            pos.ifDelete=0
            #print("停止删除状态")
        if(pos.ifDelete ==2 ):
            Delete_file(mypath, str(pos.position))#############################################
            pos.ifDelete=0
            #print("停止删除状态")
        if ind == 'x':
            	break
        if(pos.ifSend ==1):#如果在图像线程说ifsend是1了，就上传对应的图像到云端
            print(f"上传位置中",{pos.position})
            send_to_server(mypath, pos.position,IOTDA)
            pos.ifSend =0
            pos.ifDelete =2
            if str(pos.position) =='3':
               ind='x'
        
    sendobstxt()
    


class IOT_property():
    #所有的属性都在这里被定义
    def __init__(self,service_id):
        self.ifopen=1
        self.obs=0
        self.usb=0
        self.position=0
        self.ifcorrect=2# 是否准确
        self.ifsenfover=0
        self.opendetect=0#0表示是否可以前端提示扫描
        self.service_property=ServiceProperty()
        
        self.service_property.service_id = "detect"

    def sendproperty(self,device):#需要传入定义的物联网对象
        
        self.service_property.properties = {"usb": self.usb, "obs": self.obs,"position":self.position,"ifcorrect":self.ifcorrect,"ifsenfover":self.ifsenfover,"opendetect":self.opendetect,}
        services = [self.service_property]
        
        device.get_client().report_properties(services)
#所有的部分只需要修改这里的类然后sendproperty就可以了。
    
        
        


def main():
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@欢迎使用ioteeth智能口腔健康识别仪@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print("**********************************正在进行初始化********************************************************")
    Property = IOT_property("detect")  # 实例化所有的属性
    IOTDA = IOTEETH_MQTT()#初始化了device对象
    pos =Position()
    mypath = Path()  # 初始化路径对象
    path="/home/yyh/ioteeth/logtxt/"
    obs_txtpath = os.path.join(path, f'obs_path.txt')
    if os.path.exists(path):
         with open(obs_txtpath, 'w', encoding='utf-8') as f:
              pass
    
    print("等待云端下发开启指令")
    #while(1):
    #    if(IOTDA.c_c.start):
    #        IOTDA.c_c.start=0
    #        break

    

    # 创建第一个线程，并指定任务函数
    thread2 = threading.Thread(target=take_photo,args=(mypath,pos,IOTDA,Property))

    # 创建第二个线程，并指定任务函数
    thread1 = threading.Thread(target=obs,args =(mypath,pos,IOTDA,Property))

    # 启动线程
    thread1.start()
    thread2.start()

    # 等待两个线程执行结束
    thread1.join()
    thread2.join()

    print("本次扫描结束，感谢使用")
    sys.exit()
    
main()


from __future__ import absolute_import
from datetime import datetime

#自编函数库
from MatureFunction import position_judge,send_to_server,Delete_file,sendobstxt
from Speech import Speak_out,init_speak

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
import io
import struct
import socket
import numpy as np
##下面这些都是iotda的相关库)

from typing import List
import time
import logging
from iot_device_sdk_python.client.request.service_property import ServiceProperty
from iot_device_sdk_python.iot_device import IotDevice
from iot_device_sdk_python.client.request.command_response import CommandRsp
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(threadName)s - %(filename)s[%(funcName)s] - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

############################################################################################################################
HOST = "192.168.80.198"#得到ip地址

#保存对相机的一些设定与初始化
def opencap():
    cap = cv2.VideoCapture(0)#初始化相机
    if not cap.isOpened():
        Speak_out("相机连接出问题")
        exit(0)
    #设定窗口大小
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap
    
#控制类函数
class Position():
    def __init__(self):
        self.position = 0#初始化位置
        self.ifDelete = 0
        self.ifSend = 0
        
#拍摄线程
def take_photo(mypath,pos,IOTDA,Property):
   
    pic = pic_put()
    cap = opencap()
    while int(pos.position) < 3: #一直到4的时候，才会退出循环，保证程序正常结束
		
        #判断位置
        preposition =pos.position#用preposition保存之前的position值
        pos.position = position_judge(preposition,cap,Property,IOTDA,pic)##################################
        Property.position=pos.position
        #一旦识别失败，提示重新扫描
        if pos.position =='error':
            Property.ifcorrect=0
            Property.sendproperty(IOTDA.device)#上传是否扫描准确
            Speak_out("图像不符合要求，重新识别")
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
                        Speak_out("本次上传结束")
                        break
                pos.ifSend = 1
    pic.close()
#控制线程，云端交互
def obs(mypath,pos,IOTDA,Property):
    
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
        
    sendobstxt()#向云端发送目标目录
    


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
    
######################################################无线图传####################################################################

class pic_put():
    def __init__(self):
        self.h = HOST
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.h, 8000))  #
        self.connection = self.client_socket.makefile('wb')
        self.stream = io.BytesIO()

    def upload(self, frame):
        img_encode = cv2.imencode('.jpg', frame)[1]
        data_encode = np.array(img_encode)
        self.stream.write(data_encode)
        self.connection.write(struct.pack('<L', self.stream.tell()))
        self.connection.flush()
        self.stream.seek(0)
        self.connection.write(self.stream.read())
        self.stream.seek(0)
        self.stream.truncate()
        self.connection.write(struct.pack('<L', 0))

    def close(self):
        msg = 'exit'
        self.client_socket.send(msg.encode('utf-8'))
        self.connection.close()
        self.client_socket.close()

           
        


def main():
    
    Property = IOT_property("detect")  # 实例化所有的属性
    IOTDA = IOTEETH_MQTT()#初始化了device对象
    pos =Position()
    mypath = Path()  # 初始化路径对象
    
    path="/home/yyh/ioteeth/logtxt/"
    obs_txtpath = os.path.join(path, f'obs_path.txt')
    if os.path.exists(path):
         with open(obs_txtpath, 'w', encoding='utf-8') as f:
              pass
    init_speak()
    text ="欢迎使用牙齿健康识别仪"
    Speak_out(text)
  

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

    Speak_out("本次扫描结束，感谢您的使用")
    sys.exit()
    
main()

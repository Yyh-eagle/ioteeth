from __future__ import absolute_import
import logging
import time
from typing import List
import json
from iot_device_sdk_python.transport.raw_message import RawMessage
from iot_device_sdk_python.client.client_conf import ClientConf
from iot_device_sdk_python.client.connect_auth_info import ConnectAuthInfo
from iot_device_sdk_python.client.listener.default_publish_action_listener import DefaultPublishActionListener
from iot_device_sdk_python.client.listener.raw_device_message_listener import RawDeviceMessageListener
from iot_device_sdk_python.client.request.device_message import DeviceMessage
from iot_device_sdk_python.client.request.raw_device_message import RawDeviceMessage
from iot_device_sdk_python.iot_device import IotDevice
from iot_device_sdk_python.client.listener.command_listener import CommandListener
from iot_device_sdk_python.client.request.command_response import CommandRsp
from iot_device_sdk_python.client.listener.property_listener import PropertyListener
from iot_device_sdk_python.client.listener.property_listener import PropertyListener
from iot_device_sdk_python.client.request.service_property import ServiceProperty
from iot_device_sdk_python.client import iot_result
from iot_device_sdk_python.client.client_conf import ClientConf
from iot_device_sdk_python.client.connect_auth_info import ConnectAuthInfo
from iot_device_sdk_python.client.listener.command_listener \
import CommandListener
from iot_device_sdk_python.transport.raw_message_listener \
import RawMessageListener
from iot_device_sdk_python.iot_device import IotDevice
from iot_device_sdk_python.client.request.command_response import CommandRsp
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(threadName)s - %(filename)s[%(funcName)s] - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class control_command():

    def __init__(self):
        self.open = 0
        self.start = 0
        self.restart = 0
    def getopen(self):
        
        self.open=1
    def getstart(self):
        self.start=1
    def getrestart(self):
        self.restart=1
        
class MyMessageListener(RawMessageListener):
    """
    自定义topic的例子
    """
    def on_message_received(self, message: RawMessage):
        print(message.payload)
        print(f"receive message{RawMessage}")


class CommandSampleListener(CommandListener):
    """
    实现命令监听器的一个例子
    """
    def __init__(self, iot_device: IotDevice,c_c):
        """ 传入一个IotDevice实例 """
        self.device = iot_device
        self.c_c = c_c

    def on_command(self, request_id: str, service_id: str, command_name: str, paras: dict):

       
        
        ###########################在这里接入种种功能代码##########################
        print("接受云端命令成功")
        logger.info(str(paras))
        keys=paras.keys()
        for key in keys:
            if int(paras[key])==1 : 
                if str(key) =='open':
                    self.c_c.getopen()
                elif str(key)=='ifstart':
                    self.c_c.getstart()
                elif str(key) =='ifstart':
                    slef.c_c.getrestart()
        
            
        # 命令响应
        command_rsp = CommandRsp()
        command_rsp.result_code = CommandRsp.success_code()
        command_rsp.response_name = command_name
        command_rsp.paras = {"content": "成功执行功能"}
        self.device.get_client().respond_command(request_id, command_rsp)


class RawDeviceMsgListener(RawDeviceMessageListener):
    def on_raw_device_message(self, message: RawDeviceMessage):
        """
        处理平台下发的设备消息
        :param message:     设备消息内容
        """
        device_msg = message.to_device_message()
        if device_msg:
            print("on_device_message got system format:", message.payload)
        else:
            print("on_device_message:", message.payload)

        ###########################在这里接入种种功能代码##########################
        pass



#物联网云平台的一些类
class PropertySampleListener(PropertyListener):#传入的参数是面相iot的device
    def __init__(self, iot_device: IotDevice):
        """ 传入一个IotDevice实例 """
        self.device = iot_device

    def on_property_set(self, request_id: str, services: List[ServiceProperty]):
        """
        处理写属性
        :param request_id:  请求id
        :param services:    List<ServiceProperty>
        """

        """ 遍历service """
        for service_property in services:
            logger.info("on_property_set, service_id:" + service_property.service_id)#相当于在控制台上打印
            """ 遍历属性 """
            for property_name in service_property.properties:
                logger.info("set property name:" + property_name)
                logger.info("set property value:" + str(service_property.properties[property_name]))
        self.device.get_client().respond_properties_set(request_id, iot_result.SUCCESS)

    def on_property_get(self, request_id: str, service_id: str):
        """
        处理读属性。多数场景下，用户可以直接从平台读设备影子，此接口不用实现。
        但如果需要支持从设备实时读属性，则需要实现此接口。
        :param request_id:  请求id
        :param service_id:  服务id，可选
        """
        service_property = ServiceProperty()
        service_property.service_id = "smokeDetector"
        service_property.properties = {"alarm": 10, "smokeConcentration": 36, "temperature": 64, "humidity": 32}
        services = [service_property]
        self.device.get_client().respond_properties_get(request_id, services)


class IOTEETH_MQTT():
    #初始化
    def __init__(self):
        self.c_c=control_command()
        self.server_uri = "c337a64242.st1.iotda-device.cn-north-4.myhuaweicloud.com"
        self.port = 1883
        self.device_id = "661401dc2ccc1a5838804da1_ioteeth"  # 填入从云平台获取的设备id

        self.secret = "yyh614427"  # 填入从云平台获取的设备密钥
        # 发送消息
        self.connect_auth_info = ConnectAuthInfo()
        self.connect_auth_info.server_uri = self.server_uri
        self.connect_auth_info.port = self.port
        self.connect_auth_info.id = self.device_id
        self.connect_auth_info.secret = self.secret
        self.connect_auth_info.bs_mode = ConnectAuthInfo.BS_MODE_DIRECT_CONNECT

        self.client_conf = ClientConf(self.connect_auth_info)

        self.device = IotDevice(self.client_conf)
        self.listener=MyMessageListener()

        # 设置监听器接收平台下行消息
        self.device.get_client().set_raw_device_msg_listener(RawDeviceMsgListener())
        self.device.get_client().set_command_listener(CommandSampleListener(self.device,self.c_c))#commangd get
        

        # 设置属性监听器这里是独特的
        self.device.get_client().set_properties_listener(
        PropertySampleListener(self.device))  # 对象调用get——client属性，设定属性，设定属性的监听器，监听器就是对device实例化的监听器。
        if self.device.connect() != 0:
            logger.error("init failed")
            return
        logger.info("begin report message")
        self.default_publish_listener = DefaultPublishActionListener()
    #向云平台发送位置信息，这个位置信息用于触发深度学习识别并且告诉在什么目录下寻找图片
    def sendmessage(self,message):

        device_message = DeviceMessage()
        device_message.content = message
        self.device.get_client().report_device_message(device_message,self.default_publish_listener)

    def selfmessage(self,message):
        device_message = DeviceMessage()
        device_message.content = message
        my_topic = "$oc/devices/661401dc2ccc1a5838804da1_ioteeth/user/topicobs"
        #发布信息
        self.device.get_client().publish_raw_message(RawMessage(my_topic, json.dumps(message)))#这里可以输入数据
        


#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @describe : mqtt handler
# @Time    : 2022/03/18 16:21
# @Author  : ming fei.tang
import logging
from queue import Queue

import paho.mqtt.client as mqtt

__all__ = ["MQTTClient"]#只有这个类会被导入到其他的部分当中

class MQTTClient:
    #初始化函数
    def __init__(self, host, port, qos, heartbeat, client_id, username, password):
        self.host = host#MQTT的代理服务器的主机名或者ip地址？
        self.port = port#端口号1883
        self.qos = qos#可靠性级别？都有哪几个等级，会牺牲速度吗？
        self.queue = Queue()#队列对象将消息按照一定的顺序发送，发送的是什么消息，队列对象的功能是啥
        self.mqtt_client_id = client_id#这个是本地的id，用于唯一标识
        self.heartbeat = heartbeat#心跳？跟节拍有关？这个gpt也看不明白
        self.username = username#用户名和密码
        self.password = password
        self.mqtt_client = None#定义为none说明一会需要初始化
    #这个函数是对消息的处理
    def usr_on_message(self, user, data, msg):
        payload = msg.payload.decode('utf-8')#将消息按照utf-8的形式解码
        payload = payload.replace('\n', '').replace('\r', '').replace(' ', '')#从计算机的底层，将文字和英文消息转化乘数字消息，并去除空白符
        logging.debug('subscribe: %s , payload: %s, QoS = %s' % (msg.topic, payload, msg.qos))#调试语句

        self.queue.put(msg)#通常情况下，将消息放入队列中是为了异步处理，即将消息暂时存储起来，以便稍后处理。
    #订阅话题
    def usr_subscribe(self, topic):
        self.mqtt_client.subscribe(topic, self.qos)
        logging.info('subscribe the topic: %s' % topic)
    #取消订阅话题
    def usr_unsubscribe(self, topic):
        self.mqtt_client.unsubscribe(topic)
        logging.info('unsubscribe %s' % topic)
    #接受信息
    def receive_msg(self, timeout=None):
        logging.info('waiting for message.')
        if timeout is None:#检查是否设置了默认的超时时间
            timeout = self.heartbeat
        return self.queue.get(timeout=timeout)#等待timeout来获取队列中的信息，不是一个循环的过程
    #发布消息，参数：主题，消息内容，消息的质量，这个比较核心
    def usr_publish(self, topic, payload, qos, retain=False):
        self.mqtt_client.publish(topic, payload, qos, retain)
        logging.debug('public topic = %s, payload = %s , qos = %s, retain = %s' % (topic, payload, qos, retain))#输出日志信息
    #回调函数什么也不干
    def usr_log_callback(self, client, userdata, level, msg):
        # logging.info('public topic: %s ' % msg)
        pass
    #类似于开启的主函数了
    def start(self):
        if self.mqtt_client is None:#首先判断mqtt服务器有没有
            self.mqtt_client = mqtt.Client(client_id=self.mqtt_client_id)#用id来创建
            self.mqtt_client.on_log = self.usr_log_callback#回调函数有啥用啊
            self.mqtt_client.on_message = self.usr_on_message#通过调用方法，处理消息内容
            self.mqtt_client.username_pw_set(self.username, self.password)#登录信息
            self.mqtt_client.connect(self.host, self.port, self.heartbeat)#连接
            self.mqtt_client.loop_start()#开始线程
            logging.info("客户端('%s')连接成功" % self.mqtt_client_id)
        else:
            logging.error("客户端不存在")

    def stop(self):
        if self.mqtt_client is not None:
            self.mqtt_client.loop_stop()
            logging.info("客户端('%s')已经断开连接" % self.mqtt_client_id)
            self.mqtt_client.disconnect()
            self.mqtt_client = None
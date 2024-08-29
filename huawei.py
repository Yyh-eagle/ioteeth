# server_uri = "iot-mqtts.cn-north-4.myhuaweicloud.com"   # 需要改为用户保存的接入地址
# port = 8883
# device_id = "661401dc2ccc1a5838804da1_ioteeth"
# sc ="yyh614427"
# # iot平台的CA证书，用于服务端校验
# iot_ca_cert_path = "./resources/GlobalSignRSAOVSSLCA2018.crt.pem"
#
# device = IotDevice()
# device.create_by_secret(server_uri=server_uri,
#                         port=port,
#                         device_id=device_id,
#                         secret=sc,
#                         iot_cert_file=iot_ca_cert_path)
#
# if device.connect() != 0:
#     return
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

        """ code here """
        pass


def run():
    < create device code here ... >

    # 设置监听器接收平台下行消息
    device.get_client().set_raw_device_msg_listener(RawDeviceMsgListener())

    if device.connect() != 0:
        logger.error("init failed")
        return

    logger.info("begin report message")
    default_publish_listener = DefaultPublishActionListener()
    device_message = DeviceMessage()
    device_message.content = "Hello Huawei"
    # 定时上报消息
    while True:
        device.get_client().report_device_message(device_message,
                                                  default_publish_listener)
        time.sleep(5)
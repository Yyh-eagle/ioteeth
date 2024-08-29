import paho.mqtt.client as mqtt

# MQTT Broker 地址和端口
broker_address = "your_broker_address"
broker_port = 1883

# MQTT 发布的主题
publish_topic = "your_publish_topic"

# 连接到物联网平台的用户名和密码
username = "your_username"
password = "your_password"

# 连接回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # 连接成功后发布一条测试消息
        client.publish(publish_topic, "Test Message")
    else:
        print("Failed to connect, return code %d\n", rc)

# 创建 MQTT 客户端
client = mqtt.Client()

# 设置用户名和密码
client.username_pw_set(username, password)

# 设置连接回调函数
client.on_connect = on_connect

# 连接到 MQTT Broker
client.connect(broker_address, broker_port)

# 开始循环
client.loop_forever()

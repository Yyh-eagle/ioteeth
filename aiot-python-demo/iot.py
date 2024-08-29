import json
import time
import paho.mqtt.client as mqtt
from MqttSign import AuthIfo
from Final_config import IOTstage

iot =IOTstage()
productKey = iot.Product_key() # 阿里云物联网平台产品密钥
deviceName = iot.Divice_name()  # 阿里云物联网平台设备名称
deviceSecret = iot.Device_Secret() #阿里云物联网平台产品密码

# set timestamp, clientid, subscribe topic and publish topic
timeStamp = str((int(round(time.time() * 1000))))
clientId = "192.168.137.114"
subTopic = "/" + productKey + "/" + deviceName + "/user/get"
pubTopic = "/" + productKey + "/" + deviceName + "/user/update"

# set host, port
host = productKey + "iot-06z00ht27p8v5ka.mqtt.iothub.aliyuncs.com"
# instanceId = "***"
# host = instanceId + ".mqtt.iothub.aliyuncs.com"
port = 1883

# set tls crt, keepalive
tls_crt = "root.crt"
keepAlive = 300

# calculate the login auth info, and set it into the connection options
m = AuthIfo()
m.calculate_sign_time(productKey, deviceName, deviceSecret, clientId, timeStamp)
client = mqtt.Client(m.mqttClientId)
client.username_pw_set(username=m.mqttUsername, password=m.mqttPassword)
client.tls_set(tls_crt)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect aliyun IoT Cloud Sucess")
    else:
        print("Connect failed...  error code is:" + str(rc))

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print("receive message ---------- topic is : " + topic)
    print("receive message ---------- payload is : " + payload)

    if ("thing/service/property/set" in topic):
        on_thing_prop_changed(client, msg.topic, msg.payload)

def on_thing_prop_changed(client, topic, payload):
    post_topic = topic.replace("service","event")
    post_topic = post_topic.replace("set","post")
    Msg = json.loads(payload)
    params = Msg['params']
    post_payload = "{\"params\":" + json.dumps(params) + "}"
    print("reveice property_set command, need to post ---------- topic is: " + post_topic)
    print("reveice property_set command, need to post ---------- payload is: " + post_payload)
    client.publish(post_topic, post_payload)

def connect_mqtt():
    client.connect(host, port, keepAlive)
    return client

def publish_message():
    # publish 5 messages to pubTopic("/a1LhUsK****/python***/user/update")
    for i in range(5):
        message = "ABC" + str(i)
        client.publish(pubTopic, message)
        print("publish msg: " + str(i))
        print("publish msg: " + message)
        time.sleep(2)

def subscribe_topic():
    # subscribe to subTopic("/a1LhUsK****/python***/user/get") and request messages to be delivered
    client.subscribe(subTopic)
    print("subscribe topic: " + subTopic)

client.on_connect = on_connect
client.on_message = on_message
client = connect_mqtt()
client.loop_start()
time.sleep(2)

subscribe_topic()
publish_message()

while True:
    time.sleep(1)

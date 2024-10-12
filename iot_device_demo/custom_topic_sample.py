# -*- encoding: utf-8 -*-

# Copyright (c) 2020-2022 Huawei Cloud Computing Technology Co., Ltd. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
演示如何直接使用DeviceClient处理平台下发的命令
"""
import time
import logging
import json

from iot_device_sdk_python.client.client_conf import ClientConf
from iot_device_sdk_python.client.connect_auth_info import ConnectAuthInfo
from iot_device_sdk_python.iot_device import IotDevice
from iot_device_sdk_python.transport.raw_message_listener \
    import RawMessageListener
from iot_device_sdk_python.transport.raw_message import RawMessage

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(threadName)s - %(filename)s[%(funcName)s] - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# -*- encoding: utf-8 -*-

# Copyright (c) 2020-2022 Huawei Cloud Computing Technology Co., Ltd. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
演示如何直接使用DeviceClient处理平台下发的命令
"""


class MyMessageListener(RawMessageListener):
    """
    自定义topic的例子
    """
    def on_message_received(self, message: RawMessage):
        print(f"receive message{RawMessage}")


def run():
    server_uri = "c337a64242.st1.iotda-device.cn-north-4.myhuaweicloud.com"
    port = 1883
    device_id = "661401dc2ccc1a5838804da1_behind"
    secret = "lihongzhi"

    connect_auth_info = ConnectAuthInfo()
    connect_auth_info.server_uri = server_uri
    connect_auth_info.port = port
    connect_auth_info.id = device_id
    connect_auth_info.secret = secret
    connect_auth_info.bs_mode = ConnectAuthInfo.BS_MODE_DIRECT_CONNECT

    client_conf = ClientConf(connect_auth_info)

    device = IotDevice(client_conf)

    if device.connect() != 0:
        logger.error("init failed")
        return

    """ 自定义topic """
    my_topic = "$oc/devices/661401dc2ccc1a5838804da1_behind/user/topicobs"


    device.get_client().publish_raw_message(RawMessage(my_topic, json.dumps(1234444444444444444444444444)))#这里可以输入数据
    device.get_client().subscribe_topic(my_topic, 1, MyMessageListener())
    while True:
        time.sleep(5)

if __name__ == "__main__":
    run()


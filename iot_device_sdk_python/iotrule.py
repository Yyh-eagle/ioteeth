# coding: utf-8

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.auth.credentials import DerivedCredentials
from huaweicloudsdkiotda.v5.region.iotda_region import IoTDARegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkiotda.v5 import *

if __name__ == "__main__":
    # The AK and SK used for authentication are hard-coded or stored in plaintext, which has great security risks. It is recommended that the AK and SK be stored in ciphertext in configuration files or environment variables and decrypted during use to ensure security.
    # In this example, AK and SK are stored in environment variables for authentication. Before running this example, set environment variables CLOUD_SDK_AK and CLOUD_SDK_SK in the local environment
    ak = __import__('os').getenv("CLOUD_SDK_AK")
    sk = __import__('os').getenv("CLOUD_SDK_SK")

    credentials = BasicCredentials(ak, sk) \
            .with_derived_predicate(DerivedCredentials.get_default_derived_predicate()) \

    client = IoTDAClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(IoTDARegion.value_of("<YOUR REGION>")) \
        .build()

    try:
        request = CreateRoutingRuleRequest()
        subjectbody = RoutingRuleSubject(
            resource="device.message",
            event="report"
        )
        request.body = AddRuleReq(
            where="notify_data.body.topic = '$oc/devices/646c7579a5adc915f8966e8b_8514932826827763/user/testmsg'",
            select="notify_data.header as header,notify_data.body as body,'12345678901234abcd' as id",
            app_type="GLOBAL",
            subject=subjectbody,
            description="description",
            rule_name="rulename"
        )
        response = client.create_routing_rule(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)

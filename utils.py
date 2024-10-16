
import time
import os


from Final_config import Path


#华为云OBS
from obs import ObsClient
from obs import PutObjectHeader
from datetime import datetime
import traceback
def upload_to_obs(file,local_file_path, obs_object_key,now):
    obs_bucket ='ioteeth'#osb存储桶

    #构建文件的完整obs路径
    full_obs_path ='obs://{}{}{}/'.format(obs_bucket, obs_object_key,now)
    file_name = os.path.basename(file)
    full_obs_path += file_name
    #一个完整的obs目录是有obs_bucket,obs_object_key,filename组成的

    headers = PutObjectHeader()
    bucketName = obs_bucket.encode('latin-1').decode('utf-8')
    objectKey = full_obs_path.encode('latin-1').decode('utf-8')
 
    #start = datetime.now()  # 用来计时

    # 创建ObsClient实例
    obsClient = ObsClient(
        access_key_id='ZGCNBIRERUNYFPZY1JEW'.encode('latin-1').decode('utf-8'),  # 刚刚下载csv文件里面的Access Key Id
        secret_access_key='OzM4hTiyFsOEMZiowqnoIvG2NRF8gUsAZhd4VemX'.encode('latin-1').decode('utf-8'),  # 刚刚下载csv文件里面的Secret Access Key
        server='https://obs.cn-north-4.myhuaweicloud.com'.encode('latin-1').decode('utf-8') # 这里的访问域名就是我们在桶的基本信息那里记下的东西
    )
    #对已经存在的对象进行删除操作
    try:
        # 如果删除多版本对象请指定versionId,未开启多版本则为null
        versionId = 'null'
        # 删除单个对象
        resp = obsClient.deleteObject(bucketName, objectKey, versionId)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            pass
        else:
            print('删除失败，错误信息如下')
            print('requestId:', resp.requestId)
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
    except:
        print('删除失败')
        print(traceback.format_exc())
    #上传过程
    try:

        resp = obsClient.putFile(bucketName, objectKey, local_file_path,headers)
        if resp.status < 300:
            print(f"图像文件{file}上传成功")
            #create_obstxt(objectKey)#创建并写入文件
        else:
            print('上传失败')
            print('requestId:', resp.requestId)
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
    except:
        print('上传失败')
        print(traceback.format_exc())
    # 关闭obsClient
    obsClient.close()
    #end = datetime.now()
    #print(end - start)  # 打印出使用的总时间

def delete_file(directory):

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        try:
            if os.path.isfile(filepath):
                # 如果是文件，则删除
                os.remove(filepath)
               
            elif os.path.isdir(filepath):
                # 如果是目录，则递归调用删除目录中的文件
                delete_file(filepath)#递归函数，直接实现所有的文件全部删除
            if not os.listdir(directory):
               
                return
        except Exception as e:
            print(f"删除文件 {filepath} 时出错: {e}")
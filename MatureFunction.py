import numpy as np
import cv2

import time
import os
import subprocess
from Final_config import Path

import traceback
import threading
#华为云OBS
from obs import ObsClient
from obs import PutObjectHeader
from PositionDetect.util import Nerual_Detect
from datetime import datetime

"""
本文件实现的功能是保存所有在Final中出现的函数
具体函数包括：
基础功能部分：
1：显示图片 Showiamge（）
2：图片帧构成视频流Camera

"""
####################################标准流程函数########################################

#反馈式拍摄引导
def position_judge(preposition,cap,Property,IOTDA):

   
   
    print("###########################33",preposition)
    position = Camera_on(str(int(preposition)+1),cap,Property,IOTDA)
    print("this time-------------------------------------------------------------------",position)
    position_dictionary = {'0':"初始化",'1':"牙齿正面",'2':"下牙上侧",'3':"上牙下侧",'4':'结束指令'}
    
    if int(position) == int(preposition)+1:#如果满足既定的顺序
        print(f"{position_dictionary.get(str(position))}扫描完成，请拍摄{position_dictionary[str(int(position)+1)]}")
        return position
    else:
        print("位置识别错误")
        return 'error'#error表示没有按照提示扫描

#拍摄的核心函数，视频流，关键帧提取
def Camera(cap,position,numframe,numtime,var_threshold,Property,IOTDA):#最后一个参数实现了关键帧提取

    #初始化部分
    mypath = Path() #实例化路径对像
    time.sleep(0.1)# 预热摄像头

    #初始化计数变量
    frame_count =0
    start_time =None
    image_count = 0

    print("等待前端命令拍摄……")  # 开始录制
    # 定义关键帧表和阈值   
    key_frames = []
    threshold = 170 # 阈值可以根据实际情况调整
    #控制变量22
    #Property.opendetect=1
    #fProperty.sendproperty(IOTDA.device)
    # 图片流循环
    while True:
        value, frame = cap.read()
        if not value:
             print("摄像头出现了问题")
             exit(0)
        # 展示该帧
        
        cv2.imshow("Frame", frame)
        
        #键盘功能，在真实的代码中是由物联网平台发布的指令
        key = IOTDA.c_c.open
        # 等待空格键启动
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if key==1 :
            print("开始录制，并进行清晰度，亮度评判，根据帧差法选择关键帧")
            start_time = time.time()
            IOTDA.c_c.open=0
        
        elif key == 'out':
            exit(0)
       # 如果计时已开始
        if start_time is not None:
            # 检查是否超过三个有效的关键帧
            
            if len(key_frames)>=3:
                Property.opendetect=0
                #Property.sendproperty(IOTDA.device)
                return 0
            
            # 读取第一帧
            ret, prev_frame = cap.read()
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
           
            
            
            #关键帧提取:首先根据运动特性进行提取，提取得到三个关键帧后进入下一个口腔位置，每个关键帧的获取都需要经过清晰度和亮度的筛选
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 计算帧之间的差异
            frame_diff = cv2.absdiff(prev_gray, gray)
            # 应用阈值
            _, diff_threshold = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)
            # 检测关键帧
            
            if np.sum(diff_threshold) >0 and detect(frame,position)!=0:
                print(position)
                key_frames.append(frame)
                cv2.namedWindow('preview')
                cv2.moveWindow('preview', 100, 900)
                
                #对图像的一些处理工作
                image = cv2.GaussianBlur(frame, (5, 5), 0)  # 对图像进行高斯滤波
                image = perfect_reflective_white_balance(image)#白平衡处理
                #image = enhance_contrast(image)
                
          
                print("高斯滤波GAUSS BLUR")
                print("白平衡处理 WHITE BALANCE")
                image =Uplight(image)#自适应提亮
                cv2.imshow("preview",image)
                #print(mypath.cap_save_path(position,frame_count))
                cv2.imwrite(mypath.cap_save_path(position,frame_count), image)#保存图像
                image_count += 1
            prev_gray = gray
            frame_count += 1

    cv2.destroyAllWindows()

#显示图片
def Showimage(window_name, image):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


#返回次数
def Camera_on(aim_position,picam2,Property,IOTDA):

    NUM_FRAME =5#设置每隔多少帧保存一次
    NUM_TIME =5#设置每隔多少秒
    mypath =Path()
    #以frame 视频流的方式进行，每隔10帧保存一次
    x=Camera(picam2,aim_position,NUM_FRAME,NUM_TIME,35,Property,IOTDA)
    #小模型 
    if x==0:
        position = Nerual_Detect(mypath,aim_position)

    if position =='0':
        position ='bug'
    return str(position)

#############################一些图像的预处理################################
#核心算法：关键帧提取
def detect(image,position):
    if uplight_detect(image)==1 and detective(image,position)==1:
        return 1
    else: return 0
#完美反射法白平衡处理
def perfect_reflective_white_balance(img):
    # 将图像数据类型转换为 float32，以便进行计算
    src = img.astype(np.float32)
    # 计算每个通道的最大值
    max_value = np.percentile(src, 99.9, axis=(0, 1))

    # 对每个通道进行缩放
    scaled = src / max_value * 255
    scaled = np.clip(scaled, 0, 255)  # 限制数值范围避免数据溢出

    return scaled.astype(np.uint8)    
def enhance_contrast(image, alpha=1.15, beta=0):
    
    # 将图像数据类型转换为浮点型，然后进行调整
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    return adjusted

#三级提亮图片
def Uplight(image):
    print("----------------------------------------三级提亮-------------------------------------------")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_t=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    h,s,v=cv2.split(img_t)
    # 计算图像的整体亮度值（平均灰度）
    brightness = cv2.mean(gray_image)[0]#以平均灰度作为亮度的评判标准
    # 设定亮度阈值，这里以127为例
    threshold1 = 87
    threshold2 = 55

    # 三阈值提亮
    if brightness < threshold2:
        # 对亮度较暗的图像进行提亮处理
        print("二级提亮")
        v1=np.clip(cv2.add(1*v,60),0,255)
        img1=np.uint8(cv2.merge((h,s,v1)))
        
        return cv2.cvtColor(img1,cv2.COLOR_HSV2BGR) 
    elif brightness < threshold1 :
        # 对亮度较暗的图像进行提亮处理
        print("一级提亮")
        v2=np.clip(cv2.add(1*v,30),0,255)
        img2=np.uint8(cv2.merge((h,s,v2)))
        
        return cv2.cvtColor(img2,cv2.COLOR_HSV2BGR) 
    else:
        print("亮度充足")
        return image
#亮度检测
def uplight_detect(img):
 
   
    # 把图片转换为单通道的灰度图
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 获取形状以及长宽
    img_shape = gray_img.shape
    height, width = img_shape[0], img_shape[1]
    size = gray_img.size
    # 灰度图的直方图
    hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    # 计算灰度图像素点偏离均值(128)程序
    a = 0
    ma = 0
    #np.full 构造一个数组，用指定值填充其元素
    reduce_matrix = np.full((height, width), 128)
    shift_value = gray_img - reduce_matrix
    shift_sum = np.sum(shift_value)
    da = shift_sum / size
    # 计算偏离128的平均偏差
    for i in range(256):
       ma += (abs(i-128-da) * hist[i])
    m = abs(ma / size)
    k = abs(da) / m
    #print(k)
    if k[0] > 1:
       # 过亮
       if da > 0:
          print("过亮")
          return 0
       else:
          print("过暗")
          return 0
    else:
       return 1#亮度正常
#检测
def detective(image,position):
    image_gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    imageVar=cv2.Laplacian(image_gray,cv2.CV_64F).var()
    if int(position)!=3:
        if imageVar>=30:
            return 1#清晰度合格
        else: 
            print("清晰度指标为：",imageVar)
            print("清晰度不合格")
            return 0#清晰度不合格
    else:
        if imageVar>=30:
            return 1#清晰度合格
        else: 
            print("清晰度指标为：",imageVar)
            print("清晰度不合格")
            return 0#清晰度不合格
#完美反射白平衡
def c(img):
    # 将图像数据类型转换为 float32，以便进行计算
    src = img.astype(np.float32)
    # 计算每个通道的最大值
    max_value = np.percentile(src, 99.9, axis=(0, 1))

    # 对每个通道进行缩放
    scaled = src / max_value * 255
    scaled = np.clip(scaled, 0, 255)  # 限制数值范围避免数据溢出

    return scaled.astype(np.uint8)

#标定
def Undistortion(data_name, folder_path,output_folder):

    #获取标定数据mtx
    calibration_data = np.load(data_name)#先将摄像头的标定数据获取得到
    mtx, dist = calibration_data['mtx'], calibration_data['dist']#对数据进行分解

    #确保输出文件夹存在：（安全系数）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #遍历文件夹中所有图像
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg','.png','.jpeg')):
            img_path =os.path.join(folder_path,filename)
            img =cv2.imread(img_path)

            #去畸变
            undistorted_img = cv2.undistort(img.copy(), mtx, dist, None, mtx)

            #保存处理后的图像到输出文件夹
            output_path =os.path.join(output_folder,filename)
            cv2.imwrite(output_path,undistorted_img)
##################################实现数学计算的函数######################################
#计算图像的方差
def calculate_variance(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    mean = np.mean(gray)
    variance = np.mean((gray - mean) ** 2)
    return variance

    
##################################发送云存储obs##########################################
#向云服务器传送信息
def upload_to_obs(file,local_file_path, obs_bucket, obs_object_key,now,position):
    

    #构建文件的完整obs路径
    full_obs_path ='obs://{}{}{}/'.format(obs_bucket, obs_object_key,now)
    file_name = os.path.basename(file)
    full_obs_path += file_name
    #一个完整的obs目录是有obs_bucket,obs_object_key,filename组成的

    headers = PutObjectHeader()
    bucketName = obs_bucket.encode('latin-1').decode('utf-8')
    objectKey = full_obs_path.encode('latin-1').decode('utf-8')
 
    start = datetime.now()  # 用来计时

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
            create_obstxt(objectKey)#创建并写入文件
        else:
            print('上传失败')
            print('requestId:', resp.requestId)
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
    except:
        print('上传失败败')
        print(traceback.format_exc())
    # 关闭obsClient
    obsClient.close()
    end = datetime.now()
    print(end - start)  # 打印出使用的总时间
   

#向obs发送文件
def send_to_server(mypath,position,IOTDA):
   # 遍历指定目录中的所有文件和文件夹

    obs_bucket ='ioteeth'
    
    obs_object_key = mypath.obs_path(position)
    
    #选取对比度最高的两张图片作为上传的图片，关键帧提取
    for root, dirs, files in os.walk(mypath.cap_path(position)):
        for file in files:
            image =cv2.imread(os.path.join(root,file))
            contrast_values = [(file, calculate_variance(image)) for file in files]
        sorted_contrasts = sorted(contrast_values, key=lambda x: x[1], reverse=True)
        
        now = datetime.now()
        for i in range(0,3):
            file_path = os.path.join(root, sorted_contrasts[i][0])
            #为了避免多余的图像上传，每次只上传张图像
            # 上传图片文件
            
            upload_to_obs(sorted_contrasts[i][0], file_path, obs_bucket, obs_object_key,now,position)

########################################对本地缓存清除操作########################################
def Delete_file(mypath,position):
    print("进来的position",position)
    delete_file(mypath.video_save_path(position))


#清除缓存文件
def delete_file(directory):

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        try:
            if os.path.isfile(filepath):
                # 如果是文件，则删除
                os.remove(filepath)
               #print(f"已删除文件: {filepath}")
            elif os.path.isdir(filepath):
                # 如果是目录，则递归调用删除目录中的文件
                delete_file(filepath)#递归函数，直接实现所有的文件全部删除
            if not os.listdir(directory):
                print(f"目录 {directory} 现在为空，终止删除操作")
                return
        except Exception as e:
            print(f"删除文件 {filepath} 时出错: {e}")
##############################下面这些代码用于上传日志控制文件，用于和AutoDL以文件的形式进行交互
def create_obstxt(content):
    path="/home/yyh/ioteeth/logtxt/"
    obs_txtpath = os.path.join(path, f'obs_path.txt')
    
    if not os.path.exists(path):
        print("正在创建目标路径文件")
        os.makedirs(path)
        pass
    
    f = open(obs_txtpath, 'a', encoding='utf-8')
    f.write(f'{content}\n')
    f.close()
    #return f'obs_path.txt',obs_txtpath

def delete_obs_txt(path):
    print("清空本地的txt文件缓存")
    if os.path.exists(path):
        os.remove(path)
        print("删除本地缓存成功")

def sendobstxt():
    now = datetime.now()
    local_file_path='/home/yyh/ioteeth/logtxt/obs_path.txt'
    filename=f'obs_path_time{now}.txt'
    obs_bucket ='ioteeth'
    full_obs_path ='obs://{}/path_logger/'.format(obs_bucket)
    file_name = os.path.basename(filename)
    full_obs_path += file_name
    headers = PutObjectHeader()
    bucketName = obs_bucket.encode('latin-1').decode('utf-8')
    objectKey = full_obs_path.encode('latin-1').decode('utf-8')
    obsClient = ObsClient(
        access_key_id='ZGCNBIRERUNYFPZY1JEW'.encode('latin-1').decode('utf-8'),  # 刚刚下载csv文件里面的Access Key Id
        secret_access_key='OzM4hTiyFsOEMZiowqnoIvG2NRF8gUsAZhd4VemX'.encode('latin-1').decode('utf-8'),  # 刚刚下载csv文件里面的Secret Access Key
        server='https://obs.cn-north-4.myhuaweicloud.com'.encode('latin-1').decode('utf-8') # 这里的访问域名就是我们在桶的基本信息那里记下的东西
    )
    try:

        resp = obsClient.putFile(bucketName, objectKey, local_file_path,headers)
        if resp.status < 300:
            print(f"日志文件上传成功")
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
    delete_obs_txt(local_file_path)#上传之后删除

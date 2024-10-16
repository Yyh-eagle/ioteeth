
from PositionDetect.function import *
import os
from collections import Counter


# 获取指定路径下的所有图片文件路径
def get_image_paths(directory):
    image_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_paths.append(os.path.join(root, file))
    return image_paths


def Nerual_Detect(mypath,position):
    print("正在进行图像质量检测，请稍等\n")
    print(position)
    # 指定图片所在的目录路径
    image_directory = mypath.cap_path(position)

    # 获取所有图片路径
    image_paths = get_image_paths(image_directory)
    
    # 对每张图片进行预测，并统计结果
    predictions = []
    i = 0
    for img_path in image_paths:
        i+=1
        if (i%1==0):#选取一些图像来做，而不是全部
            img = cv2.imread(img_path)
            result=run(img,"/home/yyh/ioteeth/PositionDetect/models/5_183_96.78456115722656.pth")
            predictions.append(result)
    #print(predictions)
    # 统计预测结果中出现次数最多的结果
    print(predictions)
    
    most_common_prediction = Counter(predictions).most_common(1)[0][0]
    if str(most_common_prediction) == '2':
        most_common_prediction ='1'
    elif str(most_common_prediction) == '1':
        most_common_prediction ='2'
    # 打印出现次数最多的预测结果
  
    print("您的拍摄位置代号是:", most_common_prediction)
    
    return most_common_prediction




    

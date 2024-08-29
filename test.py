import cv2
import numpy as np
cap=cv2.VideoCapture(0)
fps=30
fourcc=cv2.VideoWriter_fourcc(*'XVID')
out=None


#三级提亮图片
def Uplight(image):
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
    print(k)
    if k[0] > 1:
       # 过亮
       if da > 0:
          print("过亮")
       else:
          print("过暗")
    else:
       print("亮度正常")
#清晰度检测
def detective(image):
    image_gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    imageVar=cv2.Laplacian(image_gray,cv2.CV_64F).var()
    return imageVar
while True:
    ret,frame=cap.read()
    cv2.imshow("ceshi",frame)
    key=cv2.waitKey(1)
    uplight_detect(frame)
   # cv2.imshow("up",image)
    #print(image)
    
    if key == ord('q'):
        break

# 本文件实现摄像头的标定输出的是保定矩阵
import numpy as np
import cv2
import glob
import time

# 读取大量图像，参数是一个文件夹images = glob.glob('calibration_images/*.jpg')示例
path = "/home/pi/cvcv/11/*.jpg"
img_path ="/home/pi/cvcv/1.jpg"
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
w = 8
h = 6
size = 31.2

def Glob(path):
    images = glob.glob(path)
    return images


# 彩色图转化为灰度图的通道管理
def TransferColor(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, dst=True)
    return gray_image


def Showimage(window_name, image):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def TransfferColor(image, threshold_value=128):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 二值化图像
    _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    return binary_image


# 五 重点：相机标定和畸变矫正
# 三维棋盘格创建：square_size常设置为1
def CreateChessBoard(rows, cols, square_size):
    # 生成棋盘格的三维坐标
    objp = np.zeros((rows * cols, 3), np.float32)
    # 从原点开始按照行列设置每个方块的坐标：
    objp[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2) * square_size
    return objp


# 相机标定：估计相机的内参和畸变参数。内参包括焦距，主点位置，畸变参数描述相机镜头畸变程度
# 需要拍摄多张包含已知三维坐标点的图像，并且这些点在图像中的二维坐标也要被测出来。
def CameraSet(path, rows, cols, square_size):
    objp = CreateChessBoard(rows, cols, square_size)
    # 存储物体点和图像点的列表
    objpoints = []  # 3D点的世界坐标
    imgpoints = []  # 2D点的图像坐标
    # 一般来讲,此处需要读取大量的图像
    images = Glob(path)
    i = 0
    for picture in images:
        img = cv2.imread(picture)

        # 图像滤波处理（这里使用高斯滤波，可以根据需要选择其他滤波器）
        img = cv2.GaussianBlur(img, (5, 5), 0)
        # 获取画面的中心点，长宽
        h1, w1 = img.shape[0], img.shape[1]
        gray = TransfferColor(img)  # 灰度化并二值化
        # 查找棋盘格角点：
        ret, corners = cv2.findChessboardCorners(gray, (rows, cols), None)
        if ret == True:
            i = i + 1
            print(i)
            print(picture)
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints.append(corners)
            # 将角点在图上显示
            #cv2.drawChessboardCorners(img, (rows, cols), corners, ret)
            #cv2.namedWindow('FindCorners', cv2.WINDOW_NORMAL)
            #cv2.resizeWindow('FindCorners',1280 , 960)
            #cv2.imshow('FindCorners', img)
            #cv2.waitKey(0)  # 0 表示无限等待，直到按下任意键

            # 暂停一段时间（例如，5秒）
            #time.sleep(2)

        #cv2.destroyAllWindows()
    # 相机标定：mtx是相机的内参数矩阵，dist是畸变系数
    print('正在计算')
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    # 保存表定结果
    np.savez("calibration.npz", mtx=mtx, dist=dist)

    # 畸变矫正：data——name是相机标定结果，img是待矫正的图像；output=1，则直接输出=0则保存


def Undistortion(data_name, img_path, output):
    calibration_data = np.load(data_name)
    print("calibration data:",calibration_data)
    mtx, dist = calibration_data['mtx'], calibration_data['dist']
    img = cv2.imread(img_path)
    undistorted_img = cv2.undistort(img.copy(), mtx, dist, None, mtx)
    if output == 1:
        Showimage("Undistorted Image", undistorted_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    elif output == 0:
        return undistorted_img




CameraSet(path, w, h, size)
imgg=Undistortion("calibration.npz", img_path, 0)
cv2.imwrite('output_image.jpg', imgg)
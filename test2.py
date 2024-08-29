import cv2
import numpy as np

# 打开视频文
cap=cv2.VideoCapture(0)
fps=30
fourcc=cv2.VideoWriter_fourcc(*'XVID')
out=None


# 读取第一帧
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# 定义关键帧列表和阈值
key_frames = []
threshold = 170  # 阈值可以根据实际情况调整

while True:
    # 读取下一帧
    ret, frame = cap.read()
    cv2.imshow("ceshi",frame)
    
    if not ret:
        break

    # 转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 计算帧之间的差异
    frame_diff = cv2.absdiff(prev_gray, gray)

    # 应用阈值
    _, diff_threshold = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)

    # 检测关键帧
    if np.sum(diff_threshold) > 0:
        key_frames.append(frame)
        cv2.imshow("cvv",frame)
    # 更新前一帧
    prev_gray = gray
    key=cv2.waitKey(1)
    if key == ord('q'):
        break
cap.release()

# 可以在此处处理或保存关键帧
print(f'Number of key frames detected: {len(key_frames)}')



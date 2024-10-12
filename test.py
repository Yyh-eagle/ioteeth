import cv2 
import numpy as np

cap =cv2.VideoCapture(0)
if not cap.isOpened():
        print("无法识别到相机")
while True:
	ret,frame = cap.read()
	frame = cv2.flip(frame, 1)
	cv2.line(frame,(320,100),(320,380),(0,255,0),2)
	cv2.rectangle(frame, (80, 100), (560, 380), (0, 255, 0), 2)
	cv2.imshow("Frame", frame)# 展示该帧
	k = cv2.waitKey(1) &0xFF #本地空格接受
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break

                                                                                                                                                           

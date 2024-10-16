import time



import cv2
import numpy as np


from Final_config import Path


from utils import upload_to_obs,delete_file

from Speech import Speak_out
from datetime import datetime
import os

class get_spee():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.path = Path()
        
    def image_prosess(self,position):
        while True:
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (640, 480))
            cv2.putText(frame, "Please take picture of your left side", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):
                cv2.imwrite(self.path.spee_path(position)+"spee.jpg", frame)
                
                #Speak_out("司匹曲线拍摄成功")
                self.obs_uploader(position)
                break
            if key == ord("q"):
                break
        self.cap.release()
        cv2.destroyAllWindows()
    def obs_uploader(self,position):#将图像上传至华为云obs中
        """
        position =0:左侧牙齿
        position =1:右侧牙齿
        """
        
        obs_object_key = self.path.spee_obs_path(position)
        now = datetime.now()
        print(obs_object_key)
        #递归遍历所有文件
        for root,dirs,files in os.walk(self.path.spee_path(position)):
            for file in files:
                file_path = os.path.join(root,file)
                #print(file_path)
                upload_to_obs(file,file_path,obs_object_key,now)#上传
                delete_file(self.path.spee_path(position))#清空本地缓存
          
    def delete_spee(self,path):
        delete_file(path)
        
   

   
        
if __name__ == "__main__":
    spee = get_spee()
    spee.image_prosess(0)
    
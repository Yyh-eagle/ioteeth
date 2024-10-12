
class Path(object):
#添加固有属性



    #保存视频的路径
    def video_path(self,position):
        return f"/home/yyh/ioteeth/save_path/position{position}/video{position}.avi"
        #return  f"D:\学校学习\寒假与大二下\大创项目\pythonProject\save_path\position{position}\\video{position}.avi"
    #取帧的保存路径
    def cap_save_path(self,position,frame):

        return f"/home/yyh/ioteeth/save_path/position{position}/cap/frame{frame}.jpg"
        #return f"D:\学校学习\寒假与大二下\大创项目\pythonProject\save_path\position{position}\cap\\frame{frame}.jpg"
    def cap_path(self,position):
        return  f"/home/yyh/ioteeth/save_path/position{position}/cap/"
        #return f"D:\学校学习\寒假与大二下\大创项目\pythonProject\save_path\position{position}\cap\\"
    #最终结果的保存路径
    def result_save_path(self,position):
        return f"/home/yyh/ioteeth/save_path/position{position}/results"
    #视频的文件夹
    def video_save_path(self,position):
        return f"/home/yyh/ioteeth/save_path/position{position}/"
    #标定矩阵
    def data_name(self):
        return "calibration.npz"
   

    def obs_path(self,position):#华为云的存储位置
        return f'/Picture/position{position}/'

    def obs_frame_path(self,position,iter):
        return f'obs://ioteeth/position{position}/frame{iter}.jpg'

    def obs_txt_log(self):
        return "/home/yyh/ioteeth/logtxt"

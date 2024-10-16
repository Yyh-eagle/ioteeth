
class Path(object):
#添加固有属性


   
    def cap_save_path(self,position,frame):

        return f"/home/yyh/ioteeth/save_path/position{position}/cap/frame{frame}.jpg"
        #return f"D:\学校学习\寒假与大二下\大创项目\pythonProject\save_path\position{position}\cap\\frame{frame}.jpg"
    def cap_path(self,position):
        return  f"/home/yyh/ioteeth/save_path/position{position}/cap/"
        #return f"D:\学校学习\寒假与大二下\大创项目\pythonProject\save_path\position{position}\cap\\"
    #最终结果的保存路径
    def result_save_path(self,position):
        return f"/home/yyh/ioteeth/save_path/position{position}/results"
   
   

    def obs_frame_path(self,position,iter):
        return f'obs://ioteeth/position{position}/frame{iter}.jpg'

    def obs_txt_log(self):
        return "/home/yyh/ioteeth/logtxt"
    #spee曲线采集路径
    def spee_path(self,position):
        return f"/home/yyh/ioteeth/save_path/spee/position{position}/"
    def spee_obs_path(self,position):
        return f'/Picture/spee/position{position}/'

    
    def obs_path(self,position):#华为云的存储位置
        return f'/Picture/position{position}/'


class Path(object):
#添加固有属性



    
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
        return f'obs://ioteeth/Picture/spee/position{position}/frame{iter}.jpg'


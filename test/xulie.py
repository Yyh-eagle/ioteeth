import pickle

def save_state(filename, state):
    with open(filename, 'wb') as f:
        pickle.dump(state, f)

def load_state(filename):
    with open(filename, 'rb') as f:
        state = pickle.load(f)
    return state



class IOT_property():
    #所有的属性都在这里被定义
    def __init__(self,service_id):
        self.ifopen=1
        self.obs=0
        self.usb=0
        self.position=0
        self.ifcorrect=1  # 是否准确
        self.ifsenfover=0
        self.opendetect=0#0不动，从0-1，开始扫描，从1-0关闭扫描
        self.service_property=ServiceProperty()
        #self.service_property.service_id = service_id
        self.service_property.service_id = "detect"


iot = IOT_property("172")


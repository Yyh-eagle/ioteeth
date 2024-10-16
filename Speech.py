import smbus
import time
#i2c连接
bus = smbus.SMBus(1)
#全局配置
i2c_addr = 0x30   #语音识别模块地址
date_head = 0xfd



     

  
#将字符发送到语音模块
def I2C_WriteBytes(str_):
    global i2c_addr#在函数中声明全局变量
    for ch in str_:
        try:
            bus.write_byte(i2c_addr,ch)#按每个字符ASCII码发送数据
            time.sleep(0.01)
        except:
            print("write I2C error")
#编码方式，字典->映射
EncodingFormat_Type = {
						'GB2312':0x00,
						'GBK':0X01,
						'BIG5':0x02,
						'UNICODE':0x03
						}
#对语言进行编码
def Speech_text(str_,encoding_format):
    str_ = str_.encode('gb2312')   #按gb2312码编码
    size = len(str_)+2 #获取编码长度
    DataHead = date_head 
    Length_HH = size>>8
    Length_LL = size & 0x00ff
    Commond = 0x01
    EncodingFormat = encoding_format

    Date_Pack = [DataHead,Length_HH,Length_LL,Commond,EncodingFormat]#构建数据包

    I2C_WriteBytes(Date_Pack)
    I2C_WriteBytes(str_)
#设置基础配置，与上方函数的唯一区别就在于上方函数可以更改encoding_format
def SetBase(str_):
    str_ = str_.encode('gb2312')   
    size = len(str_)+2

    DataHead = date_head
    Length_HH = size>>8
    Length_LL = size & 0x00ff
    Commond = 0x01
    EncodingFormat = 0x00

    Date_Pack = [DataHead,Length_HH,Length_LL,Commond,EncodingFormat]

    I2C_WriteBytes(Date_Pack)

    I2C_WriteBytes(str_)
#该函数根据num构造字符串并设置基础配置
#如num！=-1，则构造为[ch+num]
#num = -1，则构造为[ch]
def TextCtrl(ch,num):
    if num != -1:
        str_T = '[' + ch + str(num) + ']'
        SetBase(str_T)
    else:
        str_T = '[' + ch + ']'
        SetBase(str_T)

#获取芯片状态
ChipStatus_Type = {
                    'ChipStatus_InitSuccessful':0x4A,#初始化成功回传
                    'ChipStatus_CorrectCommand':0x41,#收到正确的命令帧回传
                    'ChipStatus_ErrorCommand':0x45,#收到不能识别命令帧回传
                    'ChipStatus_Busy':0x4E,#芯片忙碌状态回传
                    'ChipStatus_Idle':0x4F #芯片空闲状态回传                  
                }

def GetChipStatus():
    global i2c_addr
    AskState = [0xfd,0x00,0x01,0x21]
    try:
        I2C_WriteBytes(AskState)
        time.sleep(0.05)
    except:
        print("I2CRead_Write error")


    try:
        Read_result = bus.read_byte(i2c_addr)
        return Read_result
    except:
        print("I2CRead error")
        
#代码合成风格
Style_Type = {
                'Style_Single':0,#为 0，一字一顿的风格
                'Style_Continue':1#为 1，正常合成
                }#合成风格设置 [f?]

def SetStyle(num):
    TextCtrl('f',num)
    while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
        time.sleep(0.002)   


Language_Type = {
                'Language_Auto':0,#为 0，自动判断语种
                'Language_Chinese':1,#为 1，阿拉伯数字、度量单位、特殊符号等合成为中文
                'Language_English':2#为 1，阿拉伯数字、度量单位、特殊符号等合成为中文
                }#合成语种设置 [g?]

def SetLanguage(num):
	TextCtrl('g',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)

Articulation_Type = {
                'Articulation_Auto':0,#为 0，自动判断单词发音方式
                'Articulation_Letter':1,#为 1，字母发音方式
                'Articulation_Word':2#为 2，单词发音方式
                }#设置单词的发音方式 [h?]

def SetArticulation(num):
	TextCtrl('h',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)


Spell_Type = {
                'Spell_Disable':0,#为 0，不识别汉语拼音
                'Spell_Enable':1#为 1，将“拼音＋1 位数字（声调）”识别为汉语拼音，例如： hao3
                }#设置对汉语拼音的识别 [i?]

def SetSpell(num):
	TextCtrl('i',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)


Reader_Type = {
                'Reader_XiaoYan':3,#为 3，设置发音人为小燕(女声, 推荐发音人)
                'Reader_XuJiu':51,#为 51，设置发音人为许久(男声, 推荐发音人)
                'Reader_XuDuo':52,#为 52，设置发音人为许多(男声)
                'Reader_XiaoPing':53,#为 53，设置发音人为小萍(女声
                'Reader_DonaldDuck':54,#为 54，设置发音人为唐老鸭(效果器)
                'Reader_XuXiaoBao':55#为 55，设置发音人为许小宝(女童声)                
                }#选择发音人 [m?]

def SetReader(num):
	TextCtrl('m',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)


NumberHandle_Type = {
                'NumberHandle_Auto':0,#为 0，自动判断
                'NumberHandle_Number':1,#为 1，数字作号码处理
                'NumberHandle_Value':2#为 2，数字作数值处理
                }#设置数字处理策略 [n?]

def SetNumberHandle(num):
	TextCtrl('n',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)



ZeroPronunciation_Type = {
                'ZeroPronunciation_Zero':0,#为 0，读成“zero
                'ZeroPronunciation_O':1#为 1，读成“欧”音
                }#数字“0”在读 作英文、号码时 的读法 [o?]

def SetZeroPronunciation(num):
	TextCtrl('o',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)



NamePronunciation_Type = {
                'NamePronunciation_Auto':0,#为 0，自动判断姓氏读音
                'NamePronunciation_Constraint':1#为 1，强制使用姓氏读音规则
                }#设置姓名读音 策略 [r?]


def SetNamePronunciation(num):
	TextCtrl('r',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)

#设置语速 [s?] ? 为语速值，取值：0～10
def SetSpeed(speed):
	TextCtrl('s',speed)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)


#设置语调 [t?] ? 为语调值，取值：0～10
def SetIntonation(intonation):
	TextCtrl('t',intonation)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)

#设置音量 [v?] ? 为音量值，取值：0～10
def SetVolume(volume):
	TextCtrl('v',volume)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)


OnePronunciation_Type = {
                'OnePronunciation_Yao':0,#为 0，合成号码“1”时读成幺
                'OnePronunciation_Yi':1#为 1，合成号码“1”时读成一
                }#设置号码中“1”的读法 [y?]

def SetOnePronunciation(num):
	TextCtrl('y',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)


Rhythm_Type = {
                'Rhythm_Diasble':0,#为 0，“ *”和“#”读出符号
                'Rhythm_Enable':1#为 1，处理成韵律，“*”用于断词，“#”用于停顿
                }#是否使用韵律 标记“*”和“#” [z?]

def SetRhythm(num):
	TextCtrl('z',num)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)

#恢复默认的合成参数 [d] 所有设置（除发音人设置、语种设置外）恢复为默认值
def SetRestoreDefault():
	TextCtrl('d',-1)
	while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
		time.sleep(0.002)

READER = Reader_Type["Reader_XiaoYan"]
VOLUME = 2
ENCODING_FORMAT = EncodingFormat_Type["GB2312"]  
CHIP_STATUS_IDLE = ChipStatus_Type['ChipStatus_Idle']
SetSpeed(6)
SetReader(READER)
SetVolume(VOLUME)
def Speak_out(text):
    
    
    Speech_text(text, ENCODING_FORMAT)
    while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
        time.sleep(0.1)

def init_speak():
    ind = 0
    while GetChipStatus() != ChipStatus_Type['ChipStatus_Idle']:
        time.sleep(0.01)
        ind +=1
        if ind%50 == 0:
            print('初始化中')


# Speak_out('你好，我是小燕，欢迎使用！')
# Speak_out("你好我是小东，欢迎你的使用")
# Speak_out("你好我是小美，欢迎你的使用")
# Speak_out('你好，我是小燕，欢迎使用！')
# Speak_out("你好我是小东，欢迎你的使用")
# Speak_out("你好我是小美，欢迎你的使用")
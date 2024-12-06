import smbus
import time
bus = smbus.SMBus(1)

#place1 一些地址的说明
i2c_addr = 0x0f   #语音识别模块地址
asr_add_word_addr  = 0x01   #词条添加地址
asr_mode_addr  = 0x02   #识别模式设置地址，值为0-2，0:循环识别模式 1:口令模式 ,2:按键模式，默认为循环检测
asr_rgb_addr = 0x03   			#RGB灯设置地址,需要发两位，第一个直接为灯号1：蓝 2:红 3：绿 ,
                                #第二个字节为亮度0-255，数值越大亮度越高
asr_rec_gain_addr  = 0x04    #识别灵敏度设置地址，灵敏度可设置为0x00-0x7f，值越高越容易检测但是越容易误判，
                             #建议设置值为0x40-0x55,默认值为0x40                                      
asr_clear_addr = 0x05   #清除掉电缓存操作地址，录入信息前均要清除下缓存区信息
asr_key_flag = 0x06  #用于按键模式下，设置启动识别模式
asr_voice_flag = 0x07   #用于设置是否开启识别结果提示音
asr_result = 0x08  #识别结果存放地址
asr_buzzer = 0x09  #蜂鸣器控制寄存器，1位开，0位关
asr_num_cleck = 0x0a #录入词条数目校验
asr_vession = 0x0b #固件版本号
asr_busy = 0x0c #忙闲标志
#函数
def AsrAddWords(idnum,str):#录入词条
	global i2c_addr
	global asr_add_word_addr
	words = []#词条
	words.append(asr_add_word_addr)#添加词条地址
	words.append(len(str) + 2)#词条长度+2
	words.append(idnum)#对应的id号码
	for alond_word in str:#返回unicode编码
		words.append(ord(alond_word))
	words.append(0)#末尾填0
	print(words)
	for date in words:
		bus.write_byte (i2c_addr, date)
		time.sleep(0.03)

def RGBSet(R,G,B):
	global i2c_addr
	global asr_rgb_addr
	date = []
	date.append(R)
	date.append(G)
	date.append(B)

	print(date)
	bus.write_i2c_block_data (i2c_addr,asr_rgb_addr,date)

def I2CReadByte(reg):
	global i2c_addr
	bus.write_byte (i2c_addr, reg)
	time.sleep(0.05)
	Read_result = bus.read_byte (i2c_addr)
	return Read_result

def Busy_Wait():
	busy = 255
	while busy != 0:
		busy = I2CReadByte(asr_busy)
		print(asr_busy)	

'''
模式和词组具有掉电保存功能，第一次录入后续如果没有修改可以将1置位0不折行录入词条和模式
'''
cleck = 0

if 0:
    bus.write_byte_data(i2c_addr, asr_clear_addr, 0x40)#清除掉电缓存区
    Busy_Wait()				#等待模块空闲
    print("缓存区清除完毕")
    bus.write_byte_data(i2c_addr, asr_mode_addr, 0x00)#设置为循环模式
    Busy_Wait()				#等待模块空闲
    bus.write_byte_data(i2c_addr, asr_rec_gain_addr, 0x40)#设置灵敏度，建议值为0x40-0x55
    Busy_Wait()				#等待模块空闲
    bus.write_byte_data(i2c_addr, asr_voice_flag, 0)#设置开关提示音
    Busy_Wait()				#等待模块空闲
    bus.write_byte_data(i2c_addr, asr_buzzer, 0)#蜂鸣器
    Busy_Wait()				#等待模块空闲
    print("模式设置完毕完毕")
    AsrAddWords(1,"hong ya ")
    Busy_Wait()				#等待模块空闲
    AsrAddWords(2,"lv se")
    Busy_Wait()				#等待模块空闲
    AsrAddWords(3,"lan chi")
    Busy_Wait()				#等待模块空闲
    AsrAddWords(4,"guan deng")
    Busy_Wait()				#等待模块空闲
    while cleck != 4:
	    cleck = I2CReadByte(asr_num_cleck)
	    print(cleck)	


RGBSet(255,255,255)
time.sleep(1)
RGBSet(0,0,0)

AsrAddWords(1,"hong ya ")
Busy_Wait()				#等待模块空闲
AsrAddWords(2,"lv se")
Busy_Wait()				#等待模块空闲
AsrAddWords(3,"lan chi")
Busy_Wait()				#等待模块空闲
AsrAddWords(4,"guan deng")
Busy_Wait()				#等待模块空闲
while True:
    result = I2CReadByte(asr_result)
    print(result)
    if result == 1:

        print("hong ya ")
    elif result == 2:
        print("lv se")
    elif result == 3:
        print("lan chi")
    elif result == 4:
        print("guan deng")
    time.sleep(0.5)

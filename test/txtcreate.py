import os



def create_package(path):
    print("进来了")
    if os.path.exists(path):
        #删除
        pass
    os.makedirs(path)
    init_path = os.path.join(path, '__init__.txt')
    f = open(init_path, 'w', encoding='utf-8')
    f.write('# coding: utf-8\n')
    f.close()


create_package('/home/yyh/ioteeth/test/ioteet.txt')
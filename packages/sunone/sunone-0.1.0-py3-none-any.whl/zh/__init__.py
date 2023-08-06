from .search import *
# 该包一加载就执行，执行的结果是向info.txt写入token字段
def login():
    # 写文件时开始的路径为当前python文件所处的目录,info.txt与当前python文件同处于一个目录,所以可以直接写
    with open('info.txt', 'w',encoding="utf-8") as file:
        file.write('xyhlovezh1314');
        print("写入token成功......");
login();
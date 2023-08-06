# 查询关键字
def search(key):
    with open("info.txt","r",encoding='utf-8') as fs:
      if(fs.read() == "xyhlovezh1314"):
          print(f"搜索的内容为{key}");
      else:
          print("请去登录");





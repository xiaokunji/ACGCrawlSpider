import os
import re
from functools import reduce

path = "E:\pics"  # 文件夹目录
files = os.listdir(path)  # 得到文件夹下的所有文件名称
s = []
nums = 5
for file in files:  # 遍历文件夹
    s.append(file[:-4])

for i in range(2, nums):
    if str(i) not in s:
        print("未爬取页面:", i)



str="alkew/rwhegwr/"
print( str.count("/"))

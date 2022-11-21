'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 09:18:47
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-21 10:13:51
FilePath: /MiniAdmin/back/config.py
Description: 一些常量和web的配置文件
'''


import os
import sys
from loguru import logger


# 将当前目录添加到系统变量中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


LOG_LEVEL = "DEBUG"
logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
logger.add(os.path.join(BASE_DIR, "logs/logger.log"),level=LOG_LEVEL)
handler_id = logger.add(sys.stderr, level=LOG_LEVEL) 

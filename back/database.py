'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 09:45:04
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-22 16:39:35
FilePath: /MiniAdmin/back/database.py
数据库以及连接的配置.
python交流学习群号:217840699
'''

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import BASE_DIR

# 组装数据库的绝对地址
DB_DIR = os.path.join(BASE_DIR, 'miniadmin_data.db')
# 数据库访问地址
SQLALCHEMY_DATABASE_URL = "sqlite:///" + DB_DIR
# print(SQLALCHEMY_DATABASE_URL)

# 创建SQLite数据库
# engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
# 创建一个使用内存的SQLite数据库
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False,)

# 数据模型的基类
Base = declarative_base()

# 启动会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    '''
    description: 获取一个数据连接 异步fastapi下使用.
    return ssesion
    '''    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# def get_db():
#     '''
#     description: 获取数据连接,测试使用
#     return {*}
#     '''    
#     db = SessionLocal()
#     try:
#         return db
#     finally:
#         db.close()
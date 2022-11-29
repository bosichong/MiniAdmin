'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 09:16:37
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-21 09:44:08
FilePath: /MiniAdmin/back/main.py
MiniAdmin,一个简洁轻快的后台管理框架
'''

import os
import sys

# 将当前目录添加到系统变量中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 解决跨域
import uvicorn as uvicorn

from database import Base, engine
from api_v1 import router

__version__ = "0.0.1"
description = '''MiniAdmin,一个简洁轻快的后台管理框架. 🚀'''

app = FastAPI(
    title="MiniAdmin",
    description=description,
    version=__version__,
    terms_of_service="#",
    license_info={
        "name": "MIT",
        "url":  "https://opensource.org/licenses/MIT",
    },
)

# 配置允许域名
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",

]
# 配置允许域名列表、允许方法、请求头、cookie等
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

DATABASE_KEY = "miniadmin"
# 删除表，当更新表的结构时可以使用，但是会删除所有数据。慎用！！！！
# models.Base.metadata.drop_all(bind=engine)
# 在数据库中生成表结构
Base.metadata.create_all(bind=engine)


# crud.create_super_admin()


@app.get("/")
def test():
    return 'Hello MiniAdmin'


if __name__ == '__main__':
    print('少年，我看你骨骼精奇，是万中无一的编程奇才，有个程序员大佬qq群[217840699]你加下吧!维护世界和平就靠你了')
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True, )

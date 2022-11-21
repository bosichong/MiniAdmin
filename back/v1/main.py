'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 09:32:46
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-21 11:20:48
FilePath: /MiniAdmin/back/v1/main.py
v1
'''

from fastapi import APIRouter

from back.config import logger

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    responses={404: {"description": "Not found"}},  # 请求异常返回数据
)


@router.get("")
def test():
    logger.debug('Hello MiniAdmin v1')
    return 'Hello MiniAdmin v1'
'''
Author: J.sky bosichong@qq.com
Date: 2022-11-22 09:03:48
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-27 10:06:04
FilePath: /MiniAdmin/back/utils.py
工具类,密码、验证、权限验证等
python交流学习群号:217840699
'''

import os
import sys
from functools import wraps

from passlib.context import CryptContext
from pydantic import BaseSettings
from fastapi import HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from database import BASE_DIR, get_casbin_e, get_db
from models import User

LOG_LEVEL = "DEBUG"
logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
logger.add(os.path.join(BASE_DIR, "logs/logger.log"), level=LOG_LEVEL)
handler_id = logger.add(sys.stderr, level=LOG_LEVEL)

# 执行生成token的地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")


class AppTokenConfig(BaseSettings):
    """
    在终端通过以下命令生成一个新的密匙:
    openssl rand -hex 32
    加密密钥 这个很重要千万不能泄露了，而且一定自己生成并替换。
    """
    SECRET_KEY = "ededcbe81f2e015697780d536196c0baa6ea26021ad7070867e40b18a51ff8da"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # token失效时间


# 创建一个token的配置项。
APP_TOKEN_CONFIG = AppTokenConfig()

# 密码散列 pwd_context.hash(password)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    description: 校验密码
    return {*} bool
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    description: hash密码
    return {*} hashed_password
    """
    return pwd_context.hash(password)


def verify_enforce(token: str, rule):
    """
    casbin权限验证
    :param token:token
    :param rule: object ，action
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="您的帐户已锁定！",
        headers={"WWW-Authenticate": "Bearer"},
    )
    e = get_casbin_e()  # 每次都要调用，获取最新的权限规则。
    sub = get_username_by_token(token)  # token中获取用户名
    # print(sub,rule.obj,rule.act)
    if not verify_isActive(sub):
        return e.enforce(sub, rule.obj, rule.act)
    else:
        raise credentials_exception


def verify_isActive(username: str):
    """
    判断用户是否锁定
    :param username:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="当前账户不存在或已被删除！",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = next(get_db()).query(User).filter_by(username=username).first()
    if user:
        return user.is_active
    else:
        raise credentials_exception


def verify_e(e, sub, obj, act):
    return e.enforce(sub, obj, act)


def get_username_by_token(token):
    """
    从token中取出username
    :param token:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # print('获取用户名'+token)
        payload = jwt.decode(token, APP_TOKEN_CONFIG.SECRET_KEY, algorithms=[APP_TOKEN_CONFIG.ALGORITHM])
        username: str = payload.get("sub")  # 从 token中获取用户名
        return username
    except JWTError:
        raise credentials_exception


import copy


def update_array(original_array, parameters):
    '''
    拼装前端权限管理展示数据
    :param original_array:
    :param parameters:
    :return:
    '''
    result = copy.deepcopy(original_array)

    for parameter in parameters:
        # print(parameter)
        if len(parameter) <= 0:
            break
        for original in result:
            if parameter[0] == original[0]:
                result[result.index(original)] = parameter
                break
    for original in result:
        if original not in parameters:
            result[result.index(original)] = []

    return result


if __name__ == '__main__':
    original_array = [['用户管理:', '增', '删', '改', '查', '显'],
                      ['角色管理:', '增', '删', '改', '查', '显'],
                      ['资源管理:', '增', '删', '改', '查', '显'],
                      ['动作管理:', '增', '删', '改', '查', '显']]
    parameters = [['用户管理:', '查', '显'], ['动作管理:', '查', '显']]

    result = update_array(original_array, parameters)
    print(result)
    print(original_array)
    print(parameters)

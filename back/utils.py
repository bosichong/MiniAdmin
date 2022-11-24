'''
Author: J.sky bosichong@qq.com
Date: 2022-11-22 09:03:48
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-24 09:55:33
FilePath: /MiniAdmin/back/utils.py
工具类,密码、验证、权限验证等
python交流学习群号:217840699
'''

from functools import wraps
from passlib.context import CryptContext
from pydantic import BaseSettings

class AppTokenConfig(BaseSettings):
    """
    在终端通过以下命令生成一个新的密匙:
    openssl rand -hex 32
    加密密钥 这个很重要千万不能泄露了，而且一定自己生成并替换。
    """
    SECRET_KEY = "ededcbe81f2e015697780d536196c0baa6ea26021ad7070867e40b18a51ff8da"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # token失效时间


# 创建一个token的配置项。
APP_TOKEN_CONFIG = AppTokenConfig()

# 密码散列 pwd_context.hash(password)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    '''
    description: 校验密码
    return {*} bool
    '''    
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    '''
    description: hash密码
    return {*} hashed_password
    '''    
    return pwd_context.hash(password)


def verify_casbin_decorator(e,sub,obj,act):
    '''
    casein 的rbac 权限校验装饰器
    e : casbin的 enforce 验证方法
    sub : 想要访问资源的用户
    obj : 将要被访问的资源
    act : 用户对资源进行的操作
    return {*} 校验权限的结果:通过执行包装的函数,否则返回433
    '''
    
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if e.enforce(sub, obj, act):
                return fun(*args, **kwargs)
            else:
                return '433!'
        return wrapper
    return decorator


'''
Author: J.sky bosichong@qq.com
Date: 2022-11-22 09:03:48
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-27 10:06:04
FilePath: /MiniAdmin/back/utils.py
工具类,密码、验证、权限验证等
python交流学习群号:217840699
'''

from functools import wraps

from passlib.context import CryptContext
from pydantic import BaseSettings
from fastapi import HTTPException, status
from jose import JWTError, jwt

from schemas import TokenData

from fastapi.security import OAuth2PasswordBearer

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
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # token失效时间


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


def verify_casbin_decorator(e, sub, obj, act):
    """
    casein 的rbac 权限校验装饰器
    e : casbin的 enforce 验证方法
    sub : 想要访问资源的用户组
    obj : 将要被访问的资源
    act : 用户对资源进行的操作
    return {*} 校验权限的结果:通过执行包装的函数,否则返回433
    """

    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if e.enforce(sub, obj, act):
                return fun(*args, **kwargs)
            else:
                return 433

        return wrapper

    return decorator


def verify_token_wrapper():
    """定义一个token验证的装饰器"""

    def decorator(func):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登陆后尝试",
            headers={"WWW-Authenticate": "Bearer"},
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:  # 从token中解码出用户名，
                username = get_username_by_token(kwargs["token"])
                if username is None:
                    return False
                token_data = TokenData(username=username)
                if token_data.username:
                    return func(*args, **kwargs)  # 要执行的函数
                else:
                    raise credentials_exception
            except JWTError:
                raise credentials_exception

        return wrapper

    return decorator


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
        payload = jwt.decode(token, APP_TOKEN_CONFIG.SECRET_KEY, algorithms=[APP_TOKEN_CONFIG.ALGORITHM])
        username: str = payload.get("sub")  # 从 token中获取用户名
        return username
    except JWTError:
        raise credentials_exception

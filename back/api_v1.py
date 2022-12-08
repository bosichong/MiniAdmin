"""
Author: J.sky bosichong@qq.com
Date: 2022-11-21 09:32:46
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-21 11:20:48
FilePath: /MiniAdmin/back/v1/main.py
v1
"""

from datetime import datetime, timedelta
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import crud, schemas, models
from database import get_db
from schemas import Token, TokenData
from utils import verify_password, APP_TOKEN_CONFIG, oauth2_scheme, verify_token_wrapper, get_username_by_token, get_password_hash
from config import logger

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    responses={404: {"description": "Not found"}},  # 请求异常返回数据
)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    生成token
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 生成带有时间限制的token
    encoded_jwt = jwt.encode(to_encode, APP_TOKEN_CONFIG.SECRET_KEY, algorithm=APP_TOKEN_CONFIG.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str, ):
    """
    认证用户，包括检测用户是否存在，密码校验。
    :param username:
    :param password:
    :param db:
    :return: 成功返回user
    """
    user = crud.get_user_by_username(db, username=username)  # 获取用户信息
    # 用户不存在
    if not user:
        return False
    # 校验密码失败
    if not verify_password(password, user.hashed_password):
        return False
    # 成功返回user
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 获取用户,如果没有或密码错误并提示错误.
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帐号已被禁用!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=APP_TOKEN_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 生成token
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ########User相关的crud
@router.get("/user/me", response_model=schemas.User)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    返回当前用户的资料
    """
    username = get_username_by_token(token)
    user = crud.get_user_by_username(db, username)
    return user


@router.get('/user/user_by_id', response_model=schemas.User)
async def get_user_by_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    """
    获取指定id用户的资料
    :param token:
    :param db:
    :param user_id:
    :return: schemas.User
    """
    return crud.get_user_by_id(db, user_id)


@router.get('/user/get_users', response_model=schemas.Users)
async def get_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), skip: int = 0, limit: int = 10, keyword: str = ''):
    users = schemas.Users(users=crud.get_users(db, skip, limit, keyword), count=crud.get_users_count_by_keyword(db, keyword))
    return users


@router.get('/user/active_change')
async def user_active_change(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    return crud.active_change(db, user_id)


@router.get('/user/delete_user')
async def delete_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), user_id: int = 0):
    return crud.delete_user_by_id(db, user_id)


@router.post('/user/update_user')
async def update_user(user: schemas.UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), ):
    u = crud.get_user_by_id(db, user.user_id)
    u.username = user.username
    u.email = user.email
    u.sex = user.sex
    u.remark = user.remark
    u.avatar = user.avatar
    if user.password != '':
        hashed_password = get_password_hash(user.password)
        u.hashed_password = hashed_password
    try:
        db.commit()
        return True
    except:
        return False


# #############Role相关的api接口
@router.get('/role/get_roles')
async def get_roles(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_roles(db)


@router.post('/role/create_role')
async def create_role(role: schemas.Role, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), ):
    new_role = models.Role()
    new_role.name = role.name
    new_role.role_key = role.role_key
    new_role.description = role.description
    new_role.user_id = int(role.user_id)
    return crud.create_role(db, new_role)


@router.get('/role/get_role_by_id')
async def get_role_by_id(role_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_role_by_id(db, role_id)


@router.post('/role/update_role')
async def update_role_by_id(role: schemas.EditRole, token: str = Depends(oauth2_scheme),
                            db: Session = Depends(get_db)):
    new_role = models.Role()
    new_role.name = role.name
    new_role.role_key = role.role_key
    new_role.description = role.description
    return crud.update_role_by_id(db, role.old_role_id, new_role)


@router.get('/role/delete_role')
async def delete_role_by_id(role_id: int, token: str = Depends(oauth2_scheme),
                            db: Session = Depends(get_db)):
    return crud.delete_role_by_id(db, role_id)


######################################
# CasbinObject相关的api接口
######################################

@router.get('/co/get_cos')
async def get_cos(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_casbin_objects(db)


@router.post('/co/create_co')
async def create_casbin_object(co: schemas.createCasbinObject, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    new_co = models.CasbinObject()
    new_co.name = co.name
    new_co.object_key = co.object_key
    new_co.description = co.description
    new_co.user_id = co.user_id
    return crud.create_casbin_object(db, new_co)


@router.get('/co/get_co')
async def get_casbin_object(co_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_casbin_object_by_id(db, co_id)


@router.post('/co/update_co')
async def update_casbin_object_by_id(co: schemas.EditCasbinObject, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.update_casbin_object(db, co.old_co_id, co.name, co.object_key, co.description)


@router.get('/co/delete_co')
async def delete_casbin_object_by_id(co_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.delete_casbin_object_by_id(db, co_id)


######################################
# CasbinObject相关的api接口
######################################

@router.get('/ca/get_cas')
async def get_cas(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_casbin_actions(db)


@router.post('/ca/create_ca')
async def create_ca(ca: schemas.createCasbinAction, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    new_ca = models.CasbinAction()
    new_ca.name = ca.name
    new_ca.action_key = ca.action_key
    new_ca.description = ca.description
    new_ca.user_id = ca.user_id
    return crud.create_casbin_action(db, new_ca)


@router.get('/ca/get_ca')
async def get_ca(ca_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.get_casbin_action_by_id(db, ca_id)


@router.post('/ca/update_ca')
async def update_ca(ca: schemas.EditCasbinAction, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.update_casbin_action_by_id(db, ca.old_ca_id, ca.name, ca.action_key, ca.description)


@router.get('/ca/delete_ca')
async def delete_ca(ca_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return crud.delete_casbin_action_by_id(db, ca_id)


@router.get("")
async def test():
    return 'Hello MiniAdmin v1'

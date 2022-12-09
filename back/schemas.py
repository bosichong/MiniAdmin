# -*- coding: UTF-8 -*-
"""
@Author   : J.sky
@Mail     : bosichong@qq.com
@Site     : https://github.com/bosichong
@QQ交流群  : python交流学习群号:217840699
@file      :schemas.py
@time     :2022/11/29

"""
from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    username: str
    password: str
    sex: str


class User(UserBase):
    id: int
    username: str
    sex: str
    email: str
    is_active: bool
    avatar: Union[str, None] = None
    remark: Union[str, None] = None

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    user_id: int
    username: str
    password: Union[str, None] = ''
    sex: str
    email: str
    avatar: Union[str, None] = None
    remark: Union[str, None] = None


class Users(BaseModel):
    users: list[User]
    count: int


class Role(BaseModel):
    name: str
    role_key: str
    description: str
    user_id: str


class EditRole(BaseModel):
    old_role_id: int
    name: str
    role_key: str
    description: str


class createCasbinObject(BaseModel):
    name: str
    object_key: str
    description: str
    user_id: int


class EditCasbinObject(BaseModel):
    old_co_id: int
    name: str
    object_key: str
    description: str


class createCasbinAction(BaseModel):
    name: str
    action_key: str
    description: str
    user_id: int


class EditCasbinAction(BaseModel):
    old_ca_id: int
    name: str
    action_key: str
    description: str


class ChangeRole(BaseModel):
    role_id: int
    checkeds: list


class ChangeUserRole(BaseModel):
    user_id:int
    names:list[str]
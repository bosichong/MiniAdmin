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
    sex:str


class User(UserBase):
    id: int
    username: str
    sex: str

    class Config:
        orm_mode = True

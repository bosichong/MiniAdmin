'''
Author: J.sky bosichong@qq.com
Date: 2022-11-22 08:57:09
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-22 16:17:45
FilePath: /MiniAdmin/back/crud.py
crud 工具
python交流学习群号:217840699
'''
from sqlalchemy.orm import Session
from models import User,Role,CasbinObject,CasbinAction,CasbinCategory


def add_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def add_role(db: Session, role: Role):
    db.add(role)
    return role
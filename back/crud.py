'''
Author: J.sky bosichong@qq.com
Date: 2022-11-22 08:57:09
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-22 22:18:17
FilePath: /MiniAdmin/back/crud.py
crud 工具
python交流学习群号:217840699
'''
from sqlalchemy.orm import Session
from models import User, CasbinAction, CasbinObject, CasbinCategory, Role


def add_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, offset: int, limit: int):
    return db.query(User).offset(offset).limit(limit).all()


def add_role(db: Session, role: Role):
    db.add(role)
    db.commit()
    return role


def add_casbin_action(db: Session, casbinaction: CasbinAction):
    db.add(casbinaction)
    db.commit()
    return casbinaction


def add_casbinactions(db: Session, casbinactions):
    for c in casbinactions:
        db.add(c)
    db.commit()


def add_casbin_category(db: Session, casbincategory: CasbinCategory):
    db.add(casbincategory)
    db.commit()


def add_casbincategorys(db: Session, casbincategorys):
    for cc in casbincategorys:
        db.add(cc)
    db.commit()


def get_casbin_category_by_name(db: Session, name: str):
    return db.query(CasbinCategory).filter(CasbinCategory.name==name).first()


def add_casbin_object(db: Session, casbinobject: CasbinObject):
    db.add(casbinobject)
    db.commit()


def add_casbinobjects(db:Session, casbinobjects):
    for co in casbinobjects:
        db.add(co)
        
    db.commit()

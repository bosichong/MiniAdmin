'''
Author: J.sky bosichong@qq.com
Date: 2022-11-22 08:57:09
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-23 19:03:27
FilePath: /MiniAdmin/back/crud.py
crud 工具
python交流学习群号:217840699
'''
from sqlalchemy.orm import Session
from models import User, CasbinAction, CasbinObject, CasbinCategory, Role, CasbinRule

from config import logger


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

def get_role(db: Session, id: int):
    return db.query(Role).filter(Role.id == id).first()


def add_casbin_action(db: Session, casbinaction: CasbinAction):
    db.add(casbinaction)
    db.commit()
    return casbinaction


def add_casbinactions(db: Session, casbinactions):
    for c in casbinactions:
        db.add(c)
    db.commit()


def get_casbin_actions(db: Session,):
    return db.query(CasbinAction).all()


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


def get_casbin_objects(db:Session):
    return db.query(CasbinObject).all()


def add_casbin_rule(db:Session, casbinrule):
    db.add(casbinrule)
    db.commit()


def filter_casbin_rule(db:Session, casbinrule):
    '''
    description: 查询是否存在相同的policy
    return {*}
    '''    
    return db.query(CasbinRule).filter_by(ptype=casbinrule.ptype,v0=casbinrule.v0,v1=casbinrule.v1,v2=casbinrule.v2).all()


def create_casbin_rule(db:Session, crs):
    '''
    description: 添加policy到数据表中
    return {表中存在的相同数据的条目,如果有相同的policy,则不再继续添加.}
    '''    
    k = 0
    for cr in crs:
        if filter_casbin_rule(db,cr):
            k+=1
        else:
            add_casbin_rule(db, cr)
    return k

def filter_casbin_rule_g(db: Session,casbinrule):
    '''
    description: 查询表中是否存在相同的角色设置
    return {*}
    '''    
    return db.query(CasbinRule).filter_by(ptype=casbinrule.ptype,v0=casbinrule.v0,v1=casbinrule.v1).all()

def create_casbin_rule_g(db:Session, cr_g):
    '''
    description: 设置用户的权限组
    return {*} 存在返回1 不存在则增加数据并返回0
    '''
    k = filter_casbin_rule_g(db,cr_g)
    if k :
        return k
    else:
        add_casbin_rule(db,cr_g)
        return 0


def get_casbin_rule_count(db:Session):
    return db.query(CasbinRule).count()


def get_casbinrule_by_rolekey_users(db:Session,role_key):
    '''
    description: 根绝role.key返回当前组的用户
    return {*} 当前角色组的所有成员
    '''    
    crs =  db.query(CasbinRule).filter_by(ptype = 'g', v1 = role_key).all()
    users = []
    for cr in crs:
        user = get_user_by_username(db,cr.v0)
        users.append(user)
    return crs

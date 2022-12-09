"""
Author: J.sky bosichong@qq.com
Date: 2022-11-22 08:57:09
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-27 22:01:28
FilePath: /MiniAdmin/back/crud.py
crud 工具
python交流学习群号:217840699

关于CasbinRule
在本系统中的经典三元组: 访问实体 (Role)，访问资源 (CasbinObject) 和访问方法 (CasbinAction)。
若其中的一个数据的key发生修改,则应修改CasbinRule里存储的规则,因为CasbinRule里值存储字符串,所以只能自己写判断.
"""

from sqlalchemy.orm import Session
from models import User, CasbinAction, CasbinObject, Role, CasbinRule
from utils import verify_password, get_password_hash
from config import logger

import random


def create_test_data(db: Session):
    """
    添加测试数据
    :param db:
    :return:
    """

    # 创建超级管理员
    hashed_password = get_password_hash('123456')
    if not get_user_by_username(db, "miniadmin"):
        add_user(db, User(username='miniadmin', hashed_password=hashed_password, email='admin@example.com', remark='超级管理员，拥有所有权限'))
        logger.info("创建超级管理员：miniadmin,以及一些模拟数据。")
    user = get_user_by_username(db, "miniadmin")
    # 添加一些用户
    if get_users_count(db) <= 1:
        for i in range(118):
            sex = str(random.randint(0, 1))
            is_active = False
            if random.randint(0, 1): is_active = True
            k = str(i)
            u = User(username='mini' + k, hashed_password=hashed_password, email='admin' + k + '@example.com',
                     sex=sex, is_active=is_active, remark='临时测试用户')
            add_user(db, u)

    if get_role_count(db) <= 0:
        # 创建角色role
        create_role(db, Role(name='超级管理员', role_key='role_superminiadmin', description='超级管理员,拥有所有系统权限', user=user))
        create_role(db, Role(name='管理员', role_key='role_miniadmin', description='拥有大部分管理权限', user=user))
        create_role(db, Role(name='普通用户', role_key='role_generaluser', description='默认注册的用户', user=user))

    if get_casbin_action_count(db) <= 0:
        # 创建CasbinAction
        cas = [
            CasbinAction(name='增', action_key='create', description='增加数据', user=user),
            CasbinAction(name='删', action_key='delete', description='删除数据', user=user),
            CasbinAction(name='改', action_key='update', description='更新数据', user=user),
            CasbinAction(name='查', action_key='read', description='读取或查询数据', user=user),
            CasbinAction(name='显', action_key='show', description='数据相关组件的显示', user=user),
        ]
        add_casbin_actions(db, cas)

    if get_casbin_object_count(db) <= 0:
        cos = [
            CasbinObject(name='用户管理:', object_key='User', description='User表--用户相关权限', user=user, ),
            CasbinObject(name='角色管理:', object_key='Role', description='Role--角色相关权限', user=user, ),
            CasbinObject(name='资源管理:', object_key='CasbinObject', description='CasbinObject--资源相关权限', user=user, ),
            CasbinObject(name='动作管理:', object_key='CasbinAction', description='CasbinAction表--动作相关权限', user=user, ),
        ]
        add_casbin_objects(db, cos)
    if get_casbin_rule_count(db) <= 0:
        # 设置超级管理员
        role = get_role_by_id(db, 1)  # 超级管理员组
        cas = get_casbin_actions(db)  # 所有动作
        cos = get_casbin_objects(db)  # 所有资源
        crs = []
        for co in cos:
            for ca in cas:
                crs.append(CasbinRule(ptype='p', v0=role.role_key, v1=co.object_key, v2=ca.action_key))

        # 为超级管理员增加所有policy
        create_casbin_rules(db, crs)
        # 设置用户miniadmin的角色为超级管理员
        create_casbin_rule_g(db, CasbinRule(ptype='g', v0=user.username, v1=role.role_key))


def add_user(db: Session, user: User):
    """
    :param db:
    :param user:
    :return:
    """
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter_by(username=username).first()


def active_change(db: Session, user_id):
    """
    修改用户锁定
    :param db:
    :param id:
    :return:
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.is_active = not user.is_active
        db.commit()
        return True
    else:
        return False


def change_user_password(db: Session, old_password: str, new_password: str, user_id: int):
    """
    description: 输入旧密码校验,成功后,修改新密码.
    return {*}
    """
    user = get_user_by_id(db, user_id)
    if verify_password(old_password, user.hashed_password):
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
    else:
        return False


def get_users(db: Session, offset: int, limit: int, keyword: str):
    return db.query(User).filter(User.username.like("%" + keyword + "%")).offset(offset).limit(limit).all()


def get_users_count_by_keyword(db: Session, keyword: str):
    return db.query(User).filter(User.username.like("%" + keyword + "%")).count()


def get_users_count(db: Session):
    """
    return 当前系统的用户数量
    :param db:
    :return:
    """
    return db.query(User).count()


def delete_user_by_id(db: Session, user_id):
    try:
        user = db.query(User).filter_by(id=user_id).first()
        db.delete(user)
        db.commit()
        return True
    except Exception as e:
        return False


def change_user_role(db: Session, user_id, role_key):
    """
    改变用户所属的用户组
    :param db:
    :param user_id:
    :param role_key:
    :return:
    """
    user = db.query(User).filter_by(id=user_id).first()
    crs = db.query(CasbinRule).filter_by(ptype='g', v0=user.username).all()
    delete_p_casbin_rules(db, crs)  # 删除所有role
    crs = [CasbinRule(ptype='g', v0=user.username, v1=role_key), ]
    create_casbin_rules(db, crs)


# Role

def get_roles(db: Session):
    return db.query(Role).all()


def create_role(db: Session, role: Role):
    db.add(role)
    try:
        db.commit()
        return role
    except:
        return False


def get_role_count(db: Session):
    return db.query(Role).count()


def get_role_by_id(db: Session, role_id: int):
    """
    description: 根据role_id返回一个role
    return role
    """
    return db.query(Role).filter_by(id=role_id).first()


def update_role_by_id(db: Session, old_role_id, new_role):
    """
    更新role,需要更新casein_rule里的数据
    :param db:
    :param old_role_id:
    :param new_role:
    :return:
    """
    role = get_role_by_id(db, old_role_id)
    old_role_key = role.role_key
    if role:
        role.name = new_role.name
        role.role_key = new_role.role_key
        role.description = new_role.description
        db.commit()

        # 更新相关的casbin_rule关联用户组的role_key
        crs = _get_casbin_rules_by_ptype_g_v1(db, old_role_key)
        for cr in crs:
            cr.v1 = new_role.role_key
        db.commit()

        # 更新相关的casbin_rule关联资源动作的role_key
        crs = _get_casbin_rules_by_ptype_p_v0(db, old_role_key)
        for cr in crs:
            cr.v0 = new_role.role_key
        db.commit()
        return True
    else:
        return False


def delete_role_by_id(db: Session, role_id):
    """
    description: 删除role,以及相关的casbin_rule

    return {bool}
    """
    role = get_role_by_id(db, role_id)
    if role:
        # 删除casbin_rule里的用户组
        crs = _get_casbin_rules_by_ptype_g_v1(db, role.role_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        # 删除casein_rule里的相关rule
        crs = _get_casbin_rules_by_ptype_p_v0(db, role.role_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        db.delete(role)
        db.commit()
        return True
    else:
        return False


def change_role_casbinrules(db: Session, role_key: str, crs:list[CasbinRule]):
    """
    修改role角色所拥有的权限，先删除role在casbinrule里原有的所有数据，然后添加前端发来的所有新数据。
    crs是一个list,包括一组需要添加到casbinrule的规则。
    :param db:
    :param role_key:
    :param crs:
    :return: bool
    """
    try:
        delete_casbin_rules(db, role_key)
        create_casbin_rules(db, crs)
        return True
    except:
        return False



# CasbinAction 动作

def get_casbin_action_count(db: Session):
    return db.query(CasbinAction).count()


def create_casbin_action(db: Session, casbinaction: CasbinAction):
    try:
        db.add(casbinaction)
        db.commit()
        return True
    except:
        return False


def add_casbin_actions(db: Session, casbinactions):
    for c in casbinactions:
        db.add(c)
    db.commit()


def get_casbin_action_by_id(db: Session, id: int):
    return db.query(CasbinAction).filter_by(id=id).first()


def update_casbin_action_by_id(db: Session, old_id: int, name: str, action_key: str, description: str):
    """
    修改casbin_action
    :param db:
    :param old_id:
    :param name:
    :param action_key:
    :param description:
    :return:
    """
    ca = get_casbin_action_by_id(db, old_id)
    temp_key = ca.action_key
    if ca:
        ca.name = name
        ca.action_key = action_key  # 如果action_key,应当更新CasbinRule里的数据
        ca.description = description
        db.commit()
        if temp_key != action_key:
            crs = get_casbin_rules_by_act_key(db, temp_key)
            for cr in crs:
                cr.v2 = action_key
            db.commit()
        return ca
    else:
        return False


def delete_casbin_action_by_id(db: Session, ac_id: int):
    """
    删除casbin_action，同时删除casbinrule中存在的动作rule
    :param db: db
    :param ac_id: int
    :return: bool
    """
    ac = get_casbin_action_by_id(db, ac_id)
    ac_key = ac.action_key
    if ac:
        db.delete(ac)
        crs = get_casbin_rules_by_act_key(db, ac_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        return True
    else:
        return False


def get_casbin_actions(db: Session, ):
    return db.query(CasbinAction).all()


# CasbinObject 资源


def get_casbin_object_count(db: Session):
    return db.query(CasbinObject).count()


def create_casbin_object(db: Session, casbinobject: CasbinObject):
    try:
        db.add(casbinobject)
        db.commit()
        return True
    except:
        return False


def add_casbin_objects(db: Session, casbinobjects):
    for co in casbinobjects:
        db.add(co)
    db.commit()


def get_casbin_objects(db: Session):
    return db.query(CasbinObject).all()


def get_casbin_object_by_id(db: Session, id: int):
    return db.query(CasbinObject).filter_by(id=id).first()


def update_casbin_object(db: Session, old_id, name, obj_key, description):
    """
    更新casein_object
    :param db:
    :param old_id:
    :param name:
    :param obj_key:
    :param description:
    :return:
    """
    co = get_casbin_object_by_id(db, old_id)
    if co:
        temp_key = co.object_key
        co.name = name
        co.object_key = obj_key
        co.description = description
        db.commit()
        if temp_key != obj_key:
            cos = get_casbin_rules_by_obj_key(db, temp_key)
            for co in cos:
                co.v1 = obj_key
            db.commit()
        return True
    else:
        return False


def delete_casbin_object_by_id(db: Session, ac_id: int):
    """
    删除casbin_action，同时删除casbinrule中存在的动作
    :param db: db
    :param ac_id: int
    :return: bool
    """
    obj = get_casbin_object_by_id(db, ac_id)
    obj_key = obj.object_key
    if obj:
        db.delete(obj)
        crs = get_casbin_rules_by_obj_key(db, obj_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        return True
    else:
        return False


# CasbinRule 权限验证核心

def delete_casbin_rules(db, role_key):
    """
    批量删除casbinrules，成功返回条数，若返回0则表示没有存在的数据。
    :param db:
    :param role_key:
    :return:
    """
    crs = _get_casbin_rules_by_ptype_p_v0(db, role_key)
    if len(crs) > 0:
        for cr in crs:
            db.delete(cr)
        db.commit()
        return len(crs)
    else:
        return 0


def get_casbin_rules_by_obj_key(db: Session, obj_key):
    return db.query(CasbinRule).filter_by(v1=obj_key).all()


def get_casbin_rules_by_act_key(db: Session, act_key: str):
    """
    根据act_key返回一组CasbinRules
    :param db:
    :param act_key:
    :return: crs
    """
    return db.query(CasbinRule).filter_by(v2=act_key).all()


def filter_casbin_rule_by_role_key(db: Session, role_key):
    '''
    description: 
    根据role_key返回此角色role的权限数据,修改角色的权限是会重新添加数据
    return {list}
    '''
    return db.query(CasbinRule).filter_by(ptype="p", v0=role_key).all()


def filter_casbin_rule_g(db: Session, casbinrule):
    '''
    description: 查询表中是否存在相同的角色role设置
    return {*}
    '''
    return db.query(CasbinRule).filter_by(ptype=casbinrule.ptype, v0=casbinrule.v0, v1=casbinrule.v1).all()


def filter_casbin_rule(db: Session, casbinrule):
    '''
    description: 查询是否存在相同的policy
    return {*}
    '''
    return db.query(CasbinRule).filter_by(ptype=casbinrule.ptype, v0=casbinrule.v0, v1=casbinrule.v1,
                                          v2=casbinrule.v2).all()


def create_casbin_rules(db: Session, crs):
    """
    因为前端添加policy都是多条,所以接口只暴露批量添加.
    添加policy到数据表中,如果有相同的policy,则不再继续添加.
    return
    :param db:
    :param crs:
    :return: {表中存在的相同数据的条目}
    """
    k = 0
    for cr in crs:
        if filter_casbin_rule(db, cr):
            k += 1
        else:
            _add_casbin_rule(db, cr)
    return k


def create_casbin_rule_g(db: Session, cr_g):
    """
    设置用户的权限组
    :param db:
    :param cr_g: 一个casbinrule ptype="g"
    :return: 存在返回1 不存在则增加数据并返回0,并添加该用户到权限组
    """
    k = filter_casbin_rule_g(db, cr_g)
    if k:
        return k
    else:
        _add_casbin_rule(db, cr_g)
        return 0


def get_casbin_rule_count(db: Session):
    return db.query(CasbinRule).count()


def get_users_by_casbinrule_role_key(db: Session, role_key):
    '''
    description: 根据role.key返回当前组的用户
    return {*} 当前角色组的所有成员
    '''
    crs = db.query(CasbinRule).filter_by(ptype='g', v1=role_key).all()
    users = []
    for cr in crs:
        user = get_user_by_username(db, cr.v0)
        users.append(user)
    return crs


def get_casbin_rules_by_role_key(db: Session, role_key):
    '''
    description: 
    return {*} 该权限组所包括的所有权限casbinrule
    '''
    return db.query(CasbinRule).filter_by(ptype="p", v0=role_key).all()


def delete_p_casbin_rules(db: Session, roles):
    '''
    description: 删除该权限组的所有casbinrule
    return {*}
    '''
    for r in roles:
        db.delete(r)
    db.commit()


def get_casbin_rules_by_username(db: Session, username: str):
    '''
    description: 根据用户名,返回其role角色组的数据

    param {Session} db

    param {*} username str 
    
    return {*} crs
    '''
    return db.query(CasbinRule).filter_by(ptype='g', v0=username).all()


def _get_casbin_rules_by_ptype_g_v1(db: Session, role_key: str):
    '''
    description: 返回被设置的该角色的所有管理员数据,用来更新或删除这些数据.

    param {Session} db

    param {*} role_key 根绝role_key进行搜索
    
    return {*} crs
    '''
    return db.query(CasbinRule).filter_by(ptype="g", v1=role_key).all()


def _get_casbin_rules_by_ptype_p_v0(db: Session, role_key: str):
    '''
    description: 返回该角色的所有资源动作设置数据,用来更新或删除这些数据.
    param {Session} db
    param {*} role_key 根据role_key进行搜索
    return {*} crs
    '''
    return db.query(CasbinRule).filter_by(ptype='p', v0=role_key).all()


def _add_casbin_rule(db: Session, casbinrule):
    '''
    description: 增加一条casbinrule
    return {*}
    '''
    db.add(casbinrule)
    db.commit()


def _get_casbin_rules(db: Session):
    return db.query(CasbinRule).all()

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
from models import User, CasbinAction, CasbinObject, CasbinCategory, Role, CasbinRule

from utils import verify_password, get_password_hash


def create_super_admin(db: Session):
    # TODO 创建管理员
    hashed_password = get_password_hash('123456')
    add_user(db, User(username='miniadmin', hashed_password=hashed_password, email='admin@example.com', remark='管理员'))


# User

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


def get_users(db: Session, offset: int, limit: int):
    return db.query(User).offset(offset).limit(limit).all()


def delete_user_by_id(db: Session, user_id):
    user = db.query(User).filter_by(id=user_id).first()
    # user = db.query(User).filter(User.id == user_id).first()
    # user = db.query(User).where(User.id == user_id).first()
    db.delete(user)
    db.commit()
    return not user


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

def add_role(db: Session, role: Role):
    db.add(role)
    db.commit()
    return role


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
        return role
    else:
        return False


def delete_role_by_id(db: Session, role_id):
    """
    description: 删除role,以及相关的casbin_rule

    return {bool}
    """
    role = get_role_by_id(db, role_id)
    if role:
        # 删除相关的casbin_rule
        crs = _get_casbin_rules_by_ptype_g_v1(db, role.role_key)
        for cr in crs:
            db.delete(cr)
        db.commit()

        crs = _get_casbin_rules_by_ptype_p_v0(db, role.role_key)
        for cr in crs:
            db.delete(cr)
        db.commit()
        return True
    else:
        return False


def change_role_casbinrules(db: Session, role_key: str, crs):
    """
    修改role角色所拥有的权限，先删除role在casbinrule里原有的所有数据，然后添加前端发来的所有新数据。
    :param db:
    :param role_key:
    :param crs:
    :return:
    """
    delete_casbin_rules(db, role_key)
    create_casbin_rules(db, crs)


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


# CasbinAction 动作


def add_casbin_action(db: Session, casbinaction: CasbinAction):
    db.add(casbinaction)
    db.commit()
    return casbinaction


def add_casbinactions(db: Session, casbinactions):
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


# CasbinCategory 资源分类

def add_casbin_category(db: Session, casbincategory: CasbinCategory):
    db.add(casbincategory)
    db.commit()


def add_casbincategorys(db: Session, casbincategorys):
    for cc in casbincategorys:
        db.add(cc)
    db.commit()


def get_casbin_category_by_name(db: Session, name: str):
    return db.query(CasbinCategory).filter(CasbinCategory.name == name).first()


# CasbinObject 资源

def add_casbin_object(db: Session, casbinobject: CasbinObject):
    db.add(casbinobject)
    db.commit()


def add_casbinobjects(db: Session, casbinobjects):
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


# CasbinRule 权限验证核心

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
    因为前端添加policy都是多条,所以接口之暴露批量添加.
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
    :param cr_g:
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


def get_casbin_rules_by_rolekey(db: Session, role_key):
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

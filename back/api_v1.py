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

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import crud, schemas, models
from database import get_db, get_casbin_e
from schemas import Token, TokenData
from utils import verify_password, APP_TOKEN_CONFIG, oauth2_scheme, get_username_by_token, get_password_hash, verify_casbin_e, logger

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    responses={404: {"description": "Not found"}},  # 请求异常返回数据
)


######################################
# access_token 系统登陆相关的api接口
######################################

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


######################################
# User相关的api接口
######################################
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
async def update_user(user: schemas.UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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


@router.post('/user/change_user_role')
async def change_user_role(data: schemas.ChangeUserRole, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 将用户组名称改成role_key
    role_keys = []
    for name in data.names:
        role = crud.get_role_by_name(db, name)
        role_keys.append(role.role_key)
    return crud.change_user_role(db, data.user_id, role_keys)


@router.get('/user/get_user_role')
async def get_user_role(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    roles = crud.get_roles(db)
    options = []  # 所有的权限组名称
    for role in roles:
        options.append(role.name)

    checkeds = []  # 当前用户所拥有的用户组
    crs = crud.get_casbin_rules_by_username(db, user.username)
    for cr in crs:
        role = crud.get_role_by_role_key(db, cr.v1)
        checkeds.append(role.name)

    return {'options': options, 'checkeds': checkeds}


######################################
# role相关的api接口
######################################
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


@router.get('/role/get_coca')
async def get_co_ca(role_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    返回用户组role所包含的权限用于前端使用多选框来展示
    <div  v-for="(item,index) of options.value" >
        <a-checkbox-group v-model:value="checkeds.value[index]" :options="item" />
    </div>

    其中options、checkeds是两个数组，前者包括了所有的权限列表，后者只包括当前用户组所拥有的权限。
    :param role_id: 用户则的id
    :param token:
    :param db:
    :return:
    """
    cos = crud.get_casbin_objects(db)
    cas = crud.get_casbin_actions(db)
    role = crud.get_role_by_id(db, role_id)
    all_co_ca = []  # 拼装所有权限的列表
    co_key_name = {}  # 组装一个字典，里边的资源key对应name
    ca_key_name = {}  # 组装一个字典，里边的动作key对应name
    # 一个临时的资源和动作的名称数组，类似下边
    # ['用户管理', '增', '用户管理', '删', '用户管理', '改', '角色管理', '增', '角色管理', '删', '角色管理', '改']

    """
    # 群里大佬提供的算法。
    input = ['用户管理', '增', '用户管理', '删', '用户管理', '改', '用户管理', '查', '用户管理', '显', '角色管理', '增', '角色管理', '删', '角色管理', '改', '角色管理', '查', '角色管理', '显', '资源管理', '增', '资源管理', '删', '资源管理', '改', '资源管理', '查', '资源管理', '显', '动作管理', '增', '动作管理', '删', '动作管理', '改', '动作管理', '查', '动作管理', '显', '资源分类', '增', '资源分类', '删', '资源分类', '改', '资源分类', '查', '资源分类', '显']
    
    m = dict()
    key = ''
    for i in range (len(input)):
        if i % 2 == 0:
           key = input[i]
        else:
            if m.get(key) != None: 
                m[key].append(input[i])
            else:
                m[key] = [input[i]]
    
    res = []
    
    for key in m.keys():
        item = [key]
        item = item + m[key]
        res.append(item)
    
    print(res)
    
    
    """
    cks = []
    checkeds = []  # 当前用户组所拥有的权限
    for co in cos:
        coca = [co.name]
        for ca in cas:
            coca.append(ca.name)
        all_co_ca.append(coca)

    for co in cos:
        co_key_name[co.object_key] = co.name
    for ca in cas:
        ca_key_name[ca.action_key] = ca.name

    crs = crud.get_casbin_rules_by_role_key(db, role.role_key)

    for cr in crs:
        cks.append(co_key_name[cr.v1])
        cks.append(ca_key_name[cr.v2])
    # print(cks)
    temp_nams = list()
    for ck in cks:
        if len(temp_nams) == 0:
            temp_nams.append(ck)
            # print(temp_nams)
        elif temp_nams[0] == ck:
            pass
        elif ck in co_key_name.values() and ck != temp_nams[0]:
            checkeds.append(temp_nams)
            temp_nams = [ck]
        elif ck in ca_key_name.values() and ck not in temp_nams:
            temp_nams.append(ck)
            # print(temp_nams)
    checkeds.append(temp_nams)
    # print(checkeds)
    return {'options': all_co_ca, 'checkeds': checkeds}


@router.post('/role/change_role')
async def change_role(cr_data: schemas.ChangeRole, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    修改用户组所拥有的权限
    :param cr_data:
    :param token:
    :param db:
    :return:
    """
    role = crud.get_role_by_id(db, cr_data.role_id)
    cos = crud.get_casbin_objects(db)
    cas = crud.get_casbin_actions(db)
    co_name_key = {}  # 组装一个字典，里边的资源name对应key
    ca_name_key = {}  # 组装一个字典，里边的动作name对应key
    change_crs = []  # 准备要更新添加的所有casbinrule。

    for co in cos:
        co_name_key[co.name] = co.object_key
    for ca in cas:
        ca_name_key[ca.name] = ca.action_key

    for crs in cr_data.checkeds:
        if crs:
            try:
                object_key = co_name_key[crs[0]]
            except:
                return False
            cr_name = crs[0]
            # print(len(crs))
            if len(crs) <= 1:
                return False
            for cr in crs:
                # print(cr, cr_name)
                if cr != cr_name:
                    # print(role.role_key, object_key, ca_name_key[cr])
                    change_crs.append(models.CasbinRule(ptype='p', v0=role.role_key, v1=object_key, v2=ca_name_key[cr]))

    return crud.change_role_casbinrules(db, role.role_key, change_crs)


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


######################################
# Casbin 权限验证的api接口
######################################

@router.get('/get_menu')
async def get_menu_permissions(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    rules = [
        ['User', 'show'],
        ['Role', 'show'],
        ['CasbinObject', 'show'],
        ['CasbinAction', 'show'],
    ]
    menu = {}
    for r in rules:
        if verify_casbin_e(token, schemas.Casbin_rule(obj=r[0], act=r[1])):
            menu[r[0]] = True
        else:
            menu[r[0]] = False
    # print(menu)
    return menu


@router.post('/isAuthenticated')
async def isAuthenticated(rule: schemas.Casbin_rule, token: str = Depends(oauth2_scheme), ):
    """
    路由页面的权限验证接口
    :param rule:
    :param token:
    :return:
    """
    # print("路由权限验证")
    if verify_casbin_e(token, rule):
        return True
    else:
        return False


@router.post("/casbin_rule_test")
async def casbin_test(token: str = Depends(oauth2_scheme)):
    """
    一个关于权限接口的简单测试
    :param token:
    :return:
    """
    rule = schemas.Casbin_rule(obj='User', act='read')
    if verify_casbin_e(token, rule):
        return True
    else:
        return False

'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 10:55:30

LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-22 22:27:15
FilePath: /MiniAdmin/tests/test_database.py
python交流学习群号:217840699
'''

import os
import pytest
import casbin
from config import BASE_DIR
from casbin_sqlalchemy_adapter import Adapter
from database import get_db, Base, engine
import crud
from models import User, CasbinAction, CasbinObject, CasbinCategory, Role
from utils import get_password_hash, verify_password


class TestDatabase:

    def setup_class(self):
        self.db = next(get_db())
        adapter = Adapter(engine)
        Base.metadata.create_all(engine)
        model_path = os.path.join(BASE_DIR, 'rbac_model.conf')
        e = casbin.Enforcer(model_path, adapter)

    def test_database(self):
        assert 'commit' in dir(self.db)

    def test_add_user(self):
        hashed_password = get_password_hash('123456')
        # 创建用户
        user = crud.add_user(self.db, User(username='admin', hashed_password=hashed_password, email='admin@example.com', remark='管理员'))
        assert user.id > 0

    def test_get_users(self):
        users = crud.get_users(self.db, 0, 10)
        assert len(users) > 0

    def test_add_role(self):
        user = crud.get_user_by_id(self.db , 1)
        crud.add_role(self.db, Role(name='超级管理员', role_key='role_superminiadmin', description='超级管理员,拥有所有系统权限', user=user))
        crud.add_role(self.db, Role(name='管理员', role_key='role_miniadmin', description='拥有大部分管理权限', user=user))
        crud.add_role(self.db, Role(name='普通用户', role_key='role_generaluser', description='默认注册的用户', user=user))

    def test_add_casbinaction(self):
        user = crud.get_user_by_id(self.db , 1)
        cas = [
            CasbinAction(name='增', action_key='create', description='增加数据', user=user),
            CasbinAction(name='删', action_key='delete', description='删除数据', user=user),
            CasbinAction(name='改', action_key='update', description='更新数据', user=user),
            CasbinAction(name='查', action_key='read', description='读取或查询数据', user=user),
            CasbinAction(name='显', action_key='show', description='数据相关组件的显示', user=user),
        ]
        crud.add_casbinactions(self.db, cas)

    def test_add_casbincategorys(self):
        user = crud.get_user_by_id(self.db , 1)
        ccs = [
            CasbinCategory(name='用户管理', description='User表--用户相关权限', user=user),
            CasbinCategory(name='系统管理', description='Role表--角色相关权限', user=user),
        ]
        crud.add_casbincategorys(self.db, ccs)

    def test_add_casbinobjects(self):
        user = crud.get_user_by_id(self.db , 1)
        user_cc = crud.get_casbin_category_by_name(self.db ,'用户管理')
        sys_cc = crud.get_casbin_category_by_name(self.db ,'系统管理')
        cos = [
            CasbinObject(name='用户管理',object_key='User',description='User表--用户相关权限', user=user, cc=user_cc ),
            CasbinObject(name='角色管理',object_key='role',description='Role--角色相关权限', user=user, cc=sys_cc ),
            CasbinObject(name='资源管理',object_key='CasbinObject',description='CasbinObject--资源相关权限', user=user, cc=user_cc ),
            CasbinObject(name='动作管理',object_key='CasbinAction',description='CasbinAction表--动作相关权限', user=user, cc=user_cc ),
            CasbinObject(name='资源分类',object_key='CasbinCategory',description='CasbinCategory表--资源分类相关权限', user=user, cc=user_cc ),
        ]
        crud.add_casbinobjects(self.db,cos)

    def teardown_class(self):
        Base.metadata.drop_all(engine)


if __name__ == '__main__':
    pytest.main(["-vs", "back/pytests.py"])

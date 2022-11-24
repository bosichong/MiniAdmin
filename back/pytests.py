'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 10:55:30

LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-24 10:08:01
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
from models import User, CasbinAction, CasbinObject, CasbinCategory, Role,CasbinRule
from utils import get_password_hash, verify_password, verify_casbin_decorator



class TestDatabase:

    def setup_class(self):
        self.adapter = Adapter(engine)
        Base.metadata.create_all(engine)
        self.db = next(get_db())
        self.model_path = os.path.join(BASE_DIR, 'rbac_model.conf')
        # print(model_path)
        
    def get_casbin_e(self):
        return casbin.Enforcer(self.model_path, self.adapter)

    def test_database(self):
        assert 'commit' in dir(self.db)


    def test_add_user(self):
        hashed_password = get_password_hash('123456')
        # 创建用户
        user = crud.add_user(self.db, User(username='miniadmin', hashed_password=hashed_password, email='admin@example.com', remark='管理员'))
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
            CasbinObject(name='角色管理',object_key='Role',description='Role--角色相关权限', user=user, cc=sys_cc ),
            CasbinObject(name='资源管理',object_key='CasbinObject',description='CasbinObject--资源相关权限', user=user, cc=user_cc ),
            CasbinObject(name='动作管理',object_key='CasbinAction',description='CasbinAction表--动作相关权限', user=user, cc=user_cc ),
            CasbinObject(name='资源分类',object_key='CasbinCategory',description='CasbinCategory表--资源分类相关权限', user=user, cc=user_cc ),
        ]
        crud.add_casbinobjects(self.db,cos)

    def test_create_casbin_rule(self):
        # 整理资料 创建管理员的policy
        user = crud.get_user_by_id(self.db , 1)
        role = crud.get_role(self.db, 1) # 超级管理员
        cas = crud.get_casbin_actions(self.db) # 动作
        cos = crud.get_casbin_objects(self.db) # 资源
        crs =[]
        for co in cos:
            for ca in cas:
                crs.append(CasbinRule(ptype='p',v0=role.role_key,v1=co.object_key,v2=ca.action_key))
        
        # 为超级管理员增加所有policy
        k = crud.create_casbin_rule(self.db, crs)
        assert k == 0
        assert crud.get_casbin_rule_count(self.db) > 20

        # 设置用户miniadmin的角色为超级管理员
        k = crud.create_casbin_rule_g(self.db,CasbinRule(ptype = 'g',v0 = user.username, v1 = role.role_key))
        assert k == 0
        # 查询超级管理员
        crs = crud.get_casbinrule_by_rolekey_users(self.db,role.role_key)
        for cr in crs:
            admin_user = crud.get_user_by_username(self.db, cr.v0)
            assert admin_user.username == user.username # miniadmin
            assert cr.ptype =='g'
            assert cr.v0 == user.username
            assert cr.v1 == 'role_superminiadmin'


    def test_verify_casbin(self):
        e = self.get_casbin_e() # 
        user = crud.get_user_by_id(self.db , 1)
        
        @verify_casbin_decorator(e, user.username, 'User', 'delete')
        def haha():
            return True

        assert haha() # 权限通过
        

    def teardown_class(self):
        Base.metadata.drop_all(engine)
        # pass


if __name__ == '__main__':
    pytest.main(["-vs", "back/pytests.py"])

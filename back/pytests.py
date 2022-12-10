'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 10:55:30

LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-27 22:15:01
FilePath: /MiniAdmin/tests/test_database.py
python交流学习群号:217840699
'''

import os
import pytest
import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import get_db_to_T_E_S_T, engine_test, Base
import crud
from models import User, CasbinAction, CasbinObject, Role, CasbinRule
from utils import get_password_hash, verify_password, verify_casbin_decorator,\
    verify_e,BASE_DIR


class TestDatabase:

    def setup_class(self):

        Base.metadata.create_all(engine_test)
        self.db = next(get_db_to_T_E_S_T())
        self.adapter = Adapter(engine_test)
        self.model_path = os.path.join(BASE_DIR, 'rbac_model.conf')

        # 创建用户
        hashed_password = get_password_hash('123456')
        crud.add_user(self.db, User(username='miniadmin', hashed_password=hashed_password, email='admin@example.com', remark='管理员'))
        crud.add_user(self.db, User(username='test', hashed_password=hashed_password, email='test@example.com', remark='test'))
        user = crud.get_user_by_id(self.db, 1)

        # 创建角色role
        crud.create_role(self.db, Role(name='超级管理员', role_key='role_superminiadmin', description='超级管理员,拥有所有系统权限', user=user))
        crud.create_role(self.db, Role(name='管理员', role_key='role_miniadmin', description='拥有大部分管理权限', user=user))
        crud.create_role(self.db, Role(name='普通用户', role_key='role_generaluser', description='默认注册的用户', user=user))
        crud.create_role(self.db, Role(name='test', role_key='role_test', description='testrole', user=user))

        # 创建CasbinAction
        cas = [
            CasbinAction(name='增', action_key='create', description='增加数据', user=user),
            CasbinAction(name='删', action_key='delete', description='删除数据', user=user),
            CasbinAction(name='改', action_key='update', description='更新数据', user=user),
            CasbinAction(name='查', action_key='read', description='读取或查询数据', user=user),
            CasbinAction(name='显', action_key='show', description='数据相关组件的显示', user=user),
            CasbinAction(name='test', action_key='test', description='test', user=user),
        ]
        crud.add_casbin_actions(self.db, cas)

        # 创建CasbinObject

        cos = [
            CasbinObject(name='用户管理', object_key='User', description='User表--用户相关权限', user=user, ),
            CasbinObject(name='角色管理', object_key='Role', description='Role--角色相关权限', user=user, ),
            CasbinObject(name='资源管理', object_key='CasbinObject', description='CasbinObject--资源相关权限', user=user, ),
            CasbinObject(name='动作管理', object_key='CasbinAction', description='CasbinAction表--动作相关权限', user=user, ),
            CasbinObject(name='资源分类', object_key='CasbinCategory', description='CasbinCategory表--资源分类相关权限', user=user, ),
        ]
        crud.add_casbin_objects(self.db, cos)

        # 设置超级管理员
        role = crud.get_role_by_id(self.db, 1)  # 超级管理员组
        cas = crud.get_casbin_actions(self.db)  # 动作
        cos = crud.get_casbin_objects(self.db)  # 资源
        crs = []
        for co in cos:
            for ca in cas:
                crs.append(CasbinRule(ptype='p', v0=role.role_key, v1=co.object_key, v2=ca.action_key))

        # 为超级管理员增加所有policy
        k = crud.create_casbin_rules(self.db, crs)
        assert k == 0
        assert crud.get_casbin_rule_count(self.db) > 20

        # 设置用户miniadmin的角色为超级管理员
        k = crud.create_casbin_rule_g(self.db, CasbinRule(ptype='g', v0=user.username, v1=role.role_key))
        assert k == 0

        # 设置管理员
        role1 = crud.get_role_by_id(self.db, 2)  # 管理员组
        crs = []
        for i in range(1):
            for ca in cas:
                crs.append(CasbinRule(ptype='p', v0=role1.role_key, v1=cos[i].object_key, v2=ca.action_key))
        # 为帐号添加policy
        k = crud.create_casbin_rules(self.db, crs)
        assert k == 0
        # 设置用户的角色为超级管理员
        u = crud.get_user_by_id(self.db, 2)
        k = crud.create_casbin_rule_g(self.db, CasbinRule(ptype='g', v0=u.username, v1=role1.role_key))
        assert k == 0

    def get_casbin_e(self):
        return casbin.Enforcer(self.model_path, self.adapter)

    def test_database(self):
        assert 'commit' in dir(self.db)

    def test_add_user(self):
        hashed_password = get_password_hash('123456')
        user = crud.add_user(self.db,
                             User(username='test987', hashed_password=hashed_password, email='test987@example.com',
                                  remark='test987'))
        assert user.username == 'test987'
        assert user.create_time

    def test_change_user_password(self):
        user = crud.get_user_by_id(self.db, 1)
        assert crud.change_user_password(self.db, '123456', '654321', user.id)
        assert verify_password('654321', user.hashed_password)
        assert crud.change_user_password(self.db, '654321', '123456', user.id)


    def test_add_user_role(self):
        # 为用户增加角色role 添加 ptype=g 用户 角色
        # 一般角色修改只有添加这个外部动作,新建用户默认会有默认的角色,所以编辑角色管理,只是删除当前的角色,换成另外的角色.
        # 所以操作步骤,删除当前的用户的角色,然后为用户添加新的角色.
        # 为用户修改角色 搜 ptype=g 用户名称v0 修改v1
        # 删除用户角色  删除对应的ptype=g 用户 角色 的那条数据
        user = crud.get_user_by_id(self.db, 1)
        role = crud.get_role_by_id(self.db, 4)
        crud.change_user_role(self.db, user.id, role.role_key)
        e = self.get_casbin_e()

        @verify_casbin_decorator(e, user.username, 'User', 'delete')
        def haha():
            return True

        assert haha() == 433

        # 修改回超级管理员.
        role = crud.get_role_by_id(self.db, 1)
        crud.change_user_role(self.db, user.id, role.role_key)
        assert haha()

    def test_delete_user(self):
        user = crud.get_user_by_username(self.db, "test987")
        assert user.username == 'test987' and user.id == 3
        crud.delete_user_by_id(self.db, 3)
        assert crud.get_user_by_id(self.db, 3) == None

    def test_add_role(self):
        user = crud.get_user_by_id(self.db, 1)
        crud.create_role(self.db, Role(name='test888', role_key='role_test888', description='testrole888', user=user))

    def test_update_role(self):
        user = crud.get_user_by_id(self.db, 1)
        r = crud.get_role_by_id(self.db, 1)
        new_role = Role(name='超级管理员', role_key='role_testadmin88', description='超级管理员,拥有所有系统权限')
        role = crud.update_role_by_id(self.db, 1, new_role)

        crs = crud._get_casbin_rules(self.db)
        # print()
        # for cr in crs :
        #     print(cr)

    def test_delete_role(self):
        role = crud.get_role_by_id(self.db, 2)
        assert crud.delete_role_by_id(self.db, role.id)
        crs = crud._get_casbin_rules(self.db)
        # print()
        # for cr in crs :
        #     print(cr)

    def test_update_casbin_object(self):
        co = crud.get_casbin_object_by_id(self.db, 1)
        assert co.object_key == "User"
        assert crud.update_casbin_object(self.db, 1, "hello world", "hahahah", "wolaila")
        co = crud.get_casbin_object_by_id(self.db, 1)
        cr = crud.get_casbin_rules_by_obj_key(self.db, "hahahah")
        assert co.object_key == "hahahah"
        assert cr[0].v1 == "hahahah"
        assert crud.update_casbin_object(self.db, 1, "用户管理", "User", "User表--用户相关权限")
        co = crud.get_casbin_object_by_id(self.db, 1)
        cr = crud.get_casbin_rules_by_obj_key(self.db, "User")
        assert co.object_key == "User"
        assert cr[0].v1 == "User"

    def test_get_casbin_rule(self):
        # 整理资料 创建管理员的policy
        user = crud.get_user_by_id(self.db, 1)
        role = crud.get_role_by_id(self.db, 1)  # 超级管理员组

        # 查询超级管理员
        crs = crud.get_users_by_casbinrule_role_key(self.db, role.role_key)
        for cr in crs:
            admin_user = crud.get_user_by_username(self.db, cr.v0)
            assert admin_user.username == user.username  # miniadmin
            assert cr.ptype == 'g'
            assert cr.v0 == user.username
            assert cr.v1 == 'role_testadmin88'

    def test_update_casbin_action(self):
        ca = crud.get_casbin_action_by_id(self.db, 6)
        assert ca.name == 'test'
        assert crud.update_casbin_action_by_id(self.db, 6, "test1", "testkey", "test888")
        ca = crud.get_casbin_action_by_id(self.db, 6)
        assert ca.name == "test1"
        crs = crud.get_casbin_rules_by_act_key(self.db, "testkey")
        assert crs[0].v2 == "testkey"
        assert crud.update_casbin_action_by_id(self.db, 6, "test", "test", "test")
        ca = crud.get_casbin_action_by_id(self.db, 6)
        assert ca.name == "test"
        crs = crud.get_casbin_rules_by_act_key(self.db, "test")
        assert crs[0].v2 == "test"

    def test_delete_casbin_action(self):
        ca = crud.get_casbin_action_by_id(self.db, 6)
        assert ca.name == "test"
        assert crud.delete_casbin_action_by_id(self.db, 6)
        assert not crud.get_casbin_action_by_id(self.db, 6)
        assert not crud.get_casbin_rules_by_act_key(self.db, "test")

    def test_change_role_casbin_rules(self):
        user = crud.get_user_by_id(self.db, 2)
        assert user.username == "test"
        assert not crud.create_casbin_rule_g(self.db, CasbinRule(ptype="g", v0=user.username, v1="role_miniadmin"))
        e = self.get_casbin_e()

        @verify_casbin_decorator(e, user.username, 'role_test', 'delete')
        def haha():
            return True

        assert haha() == 433
        # 目前只是把test用户添加到管理员角色组，但是管理员组并没有任何权限。先添加User的管理权限。
        role = crud.get_role_by_id(self.db, 2)  # 管理员组
        cas = crud.get_casbin_actions(self.db)  # 动作
        cos = crud.get_casbin_objects(self.db)  # 资源
        crs = []

        for i in range(1):
            for ca in cas:
                crs.append(CasbinRule(ptype='p', v0=role.role_key, v1=cos[i].object_key, v2=ca.action_key))
        assert crud.create_casbin_rules(self.db, crs) == 0
        e = self.get_casbin_e()

        @verify_casbin_decorator(e, user.username, 'User', 'delete')
        def haha():
            return True

        assert haha() != 433
        crs = []
        for co in cos:
            for ca in cas:
                crs.append(CasbinRule(ptype='p', v0=role.role_key, v1=co.object_key, v2=ca.action_key))

        crud.change_role_casbinrules(self.db, role.role_key, crs)  # 为test添加所有权限！
        # self.print_crs()
        e = self.get_casbin_e()

        @verify_casbin_decorator(e, user.username, 'CasbinCategory', 'delete')
        def haha():
            return True

        assert haha() != 433  # 这里应该是通过

    def print_crs(self):
        crs = crud._get_casbin_rules(self.db)
        print()
        for cr in crs:
            print(cr)

    def test_verify_casbin(self):
        e = self.get_casbin_e()  # 使用前调用,刷新策略数据,防止验证失败.
        user = crud.get_user_by_id(self.db, 1)

        @verify_casbin_decorator(e, user.username, 'User', 'delete')
        def haha():
            return True

        @verify_casbin_decorator(e, user.username, 'User', 'd')
        def haha1():
            return True

        assert haha()  # 权限通过
        assert haha1() == 433  # 权限没有通过

    def teardown_class(self):
        Base.metadata.drop_all(engine_test)
        # pass


if __name__ == '__main__':
    pytest.main(["-vs", "back/pytests.py"])

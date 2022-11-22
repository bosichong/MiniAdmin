'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 10:55:30

LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-22 16:42:12
FilePath: /MiniAdmin/tests/test_database.py
python交流学习群号:217840699
'''

import os, sys
import pytest
from fastapi import Depends
from sqlalchemy.orm import Session
import casbin
from casbin_sqlalchemy_adapter import CasbinRule
from config import BASE_DIR
from casbin_sqlalchemy_adapter import Adapter
from database import get_db, Base, engine
import crud
from models import User,Role,CasbinObject,CasbinAction,CasbinCategory
from utils import get_password_hash, verify_password


class TestDatabase:

    def setup_class(self):
        self.db = next(get_db())
        adapter = Adapter(engine)
        Base.metadata.create_all(engine)
        model_path = os.path.join(BASE_DIR,'rbac_model.conf')
        e = casbin.Enforcer(model_path, adapter)

        
    def test_database(self):
        assert 'commit' in dir(self.db)


    def test_add_user(self):
        hashed_password  = get_password_hash('123456')
        # 创建用户
        user = crud.add_user(self.db,User(username='admin',hashed_password=hashed_password,email='admin@example.com',remark='管理员'))
        assert user.id > 0

    # def test_add_role(self):
    #     add_role(self.conn,Role(name='管理员',role_key='kkk888',description='kkk888',user_id='1'))

    def teardown_class(self):
        Base.metadata.drop_all(engine)
        print('删除所有表!')


if __name__ == '__main__':
    pytest.main(["-vs", "back/tests.py"])
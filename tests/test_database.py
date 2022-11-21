'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 10:55:30

LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-21 17:15:01
FilePath: /MiniAdmin/tests/test_database.py
python交流学习群号:217840699
'''

import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import pytest
from fastapi import Depends
from sqlalchemy.orm import Session
from back.database import get_db, Base,engine


class TestDatabase:

    def setup_class(self):
        self.conn = Session(Depends(get_db))
        Base.metadata.create_all(engine)
        print('创建数据和表')

        
    def test_database(self):
        assert 'add' in dir(self.conn)

    def test_add_user(self):
        pass


    def teardown_class(self):
        Base.metadata.drop_all(engine)
        print('删除所有表!')


if __name__ == '__main__':
    pytest.main(["-vs", "tests/test_database.py"])
'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 14:41:49
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-21 17:17:56
FilePath: /MiniAdmin/back/models.py
python交流学习群号:217840699
model,sub, obj, act 表示经典三元组: 访问实体 (Subject)，访问资源 (Object) 和访问方法 (Action)。
'''

from datetime import datetime 
from back.database import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='用户ID')
    username = Column(String(32), nullable=False, index=True, unique=True, comment='用户昵称')
    hashed_password = Column(String(128), nullable=False, comment='用户密码')
    sex = Column(String(128), nullable=False, commeng='用户性别')
    email = Column(String(128), nullable=False, unique=True, comment='用户邮箱')
    avatar = Column(String(128), comment='用户头像')
    status = Column(Integer, nullable=False, comment='帐号状态:0正常 1停用')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(128), nullable=False, comment='备注')

    roles = relationship('Role', uselist=True, back_populates='user')
    cobs = relationship('CasbinObjectAction', uselist=True, back_populates='user')
    ccs = relationship('CasbinCategory', uselist=True, back_populates='user')


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='角色id')
    name = Column(String(32), nullable=False, comment='角色名称')
    description = Column(String(128), nullable=True, comment='角色描述')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True, comment='创建者')
    user = relationship('User', back_populates='roles')


class CasbinObjectAction(Base):
    __tablename__ = 'casbin_objects_action'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(String(128), comment='资源类型')
    name = Column(String(128), nullable=False, unique=True, comment='资源名称')
    description = Column(String(128), nullable=True, comment='资源描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cobs')


class CasbinCategory(Base):
    __tablename__ = 'casbin_category'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='分类名称')
    description = Column(String(128), nullable=True, comment='分类描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='ccs')



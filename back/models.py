'''
Author: J.sky bosichong@qq.com
Date: 2022-11-21 14:41:49
LastEditors: J.sky bosichong@qq.com
LastEditTime: 2022-11-26 11:20:42
FilePath: /MiniAdmin/back/models.py
python交流学习群号:217840699
model,sub, obj, act 表示经典三元组: 访问实体 (Subject)，访问资源 (Object) 和访问方法 (Action)。
'''

from datetime import datetime
from database import Base
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    # 若有多个类指向同一张表，那么在后边的类需要把 extend_existing设为True，表示在已有列基础上进行扩展
    # 或者换句话说，sqlalchemy 允许类是表的字集，如下：
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(32), nullable=False, unique=True, comment='用户昵称')
    hashed_password = Column(String(128), nullable=False, comment='用户密码')
    sex = Column(String(1), nullable=False, default='0', comment='用户性别')
    email = Column(String(128), nullable=False, unique=True, comment='用户邮箱')
    status = Column(Integer, nullable=False, default=0, comment='帐号状态:0正常 1停用')
    avatar = Column(String(128), comment='用户头像')
    remark = Column(String(128), comment='备注')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    roles = relationship('Role', uselist=True, back_populates='user')
    cos = relationship('CasbinObject', uselist=True, back_populates='user')
    cas = relationship('CasbinAction', uselist=True, back_populates='user')
    ccs = relationship('CasbinCategory', uselist=True, back_populates='user')


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='角色id')
    name = Column(String(32), nullable=False, unique=True, comment='角色名称')
    role_key = Column(String(128), nullable=False, unique=True, comment='角色标识')
    description = Column(String(128), nullable=False, comment='角色描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='roles')


class CasbinObject(Base):
    __tablename__ = 'casbin_object'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='资源名称')
    object_key = Column(String(128), nullable=False, unique=True, comment='资源标识')
    description = Column(String(128), nullable=True, comment='资源描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cos')

    casbin_category_id = Column(Integer, ForeignKey('casbin_category.id'), nullable=False, comment='所属分类')
    cc = relationship('CasbinCategory', back_populates='cos')


class CasbinAction(Base):
    __tablename__ = 'casbin_action'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='动作名称')
    action_key = Column(String(128), nullable=False, unique=True, comment='动作标识')
    description = Column(String(128), nullable=True, comment='动作描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='cas')


class CasbinCategory(Base):
    __tablename__ = 'casbin_category'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='分类名称')
    description = Column(String(128), nullable=True, comment='分类描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='ccs')

    cos = relationship('CasbinObject', uselist=True, back_populates='cc')


class CasbinRule(Base):
    __tablename__ = "casbin_rule"

    id = Column(Integer, primary_key=True)
    ptype = Column(String(255))
    v0 = Column(String(255))
    v1 = Column(String(255))
    v2 = Column(String(255))
    v3 = Column(String(255))
    v4 = Column(String(255))
    v5 = Column(String(255))

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ", ".join(arr)

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))

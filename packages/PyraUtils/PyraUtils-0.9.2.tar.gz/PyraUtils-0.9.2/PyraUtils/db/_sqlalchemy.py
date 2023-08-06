
# 导入SQLAlchemy相关模块
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class DBManager:
    # # 测试封装类的方法(推荐是使用ORM的方法来操作映射类而不是SQL语句)

    # # 创建封装类的实例
    # db_manager = DBManager()

    # # 执行建表语句
    # db_manager.execute('create table if not EXISTS user (id int PRIMARY KEY auto_increment,name char (32), age int);')

    # # 执行插入语句
    # db_manager.execute('insert into user values (1, "Alice", 18);')

    # # 执行查询语句
    # result = db_manager.execute('select * from user;')
    # print(result.fetchall())

    # # 执行删除语句
    # db_manager.execute('delete from user where id = 1;')

    # # 执行删表语句
    # db_manager.execute('drop table user;')
    def __init__(self):
        # 创建会话类
        # 创建连接引擎
        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/test?charset=utf8')
        self.Session = sessionmaker(bind=engine)
    
    def execute(self, sql):
        # 执行SQL语句
        # 创建会话对象
        session = self.Session()
        # 执行SQL语句
        result = session.execute(sql)
        # 提交事务
        session.commit()
        # 关闭会话
        session.close()
        # 返回结果
        return result

# 定义ORM的类
class ORMManager:
    # # 测试ORM的类的方法

    # # 定义映射类
    # from sqlalchemy import create_engine, Column, Integer, String
    #
    # class User(Base):
    #     __tablename__ = 'user' # 表名
    #     id = Column(Integer, primary_key=True) # 主键
    #     name = Column(String(20)) # 姓名
    #     age = Column(Integer) # 年龄


    # # 创建ORM的类的实例
    # orm_manager = ORMManager()

    # # 添加用户Alice，年龄18岁
    # user1 = User(name='Alice', age=18) # 创建对象
    # orm_manager.add(user1) # 添加对象

    # # 查询用户Alice的信息
    # result = orm_manager.query(User, name='Alice') # 查询对象列表
    # for user in result:
    #     print(user.name, user.age) # 打印属性

    # # 修改用户Alice的年龄为19岁
    # orm_manager.update(User, condition={'name': 'Alice'}, age=19) # 更新对象

    # # 删除用户Alice的信息
    # orm_manager.delete(User, name='Alice') # 删除对象

    def __init__(self):
        # 创建会话类
        # 创建连接引擎
        engine = create_engine('mysql+pymysql://root:123456@localhost:3306/test?charset=utf8')
        # 创建基类
        Base = declarative_base()
        self.Session = sessionmaker(bind=engine)
    
    def add(self, obj):
        # 添加对象
        # 创建会话对象
        session = self.Session()
        # 添加对象
        session.add(obj)
        # 提交事务
        session.commit()
        # 关闭会话
        session.close()
    
    def query(self, cls, **kwargs):
        # 查询对象
        # 创建会话对象
        session = self.Session()
        # 查询对象
        result = session.query(cls).filter_by(**kwargs).all()
        # 关闭会话
        session.close()
        # 返回结果
        return result
    
    def update(self, cls, condition, **kwargs):
        # 更新对象
        # 创建会话对象
        session = self.Session()
        # 查询对象
        obj = session.query(cls).filter_by(**condition).first()
        if obj:
            # 更新属性
            for key, value in kwargs.items():
                setattr(obj, key, value)
            # 提交事务
            session.commit()
            print('Update success')
        else:
            print('No such object')
        # 关闭会话
        session.close()
    
    def delete(self, cls, **kwargs):
        # 删除对象
        # 创建会话对象
        session = self.Session()
        # 查询对象
        obj = session.query(cls).filter_by(**kwargs).first()
        if obj:
            # 删除对象
            session.delete(obj)
            # 提交事务
            session.commit()
            print('Delete success')
        else:
            print('No such object')
        # 关闭会话
        session.close()

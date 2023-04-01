"""
数据库配置文件: databases.py, 主要完成对数据库的连接
"""

from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

# mysql连接字符串是："mysql+pymysql://用户名:密码@主机IP:端口/数据库名?charset=utf8"
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_db/sqlite_app.db"
engine = create_engine(
    # sqlite3数据库本身并非一个网络数据库，其默认只能在同一线程中使用，如果不设定该标记，则SQLAlchemy会提示错误
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 通过创建一个SessionLocal变量，将当前数据库的连接保存于其中
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # model.py 文件要用它来定义数据库表

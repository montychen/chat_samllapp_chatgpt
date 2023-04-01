"""
数据库中表对应的模型文件：models.py
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean  # type: ignore
# 导入在database.py文件创建的基类Base. 如果提示导入警告，可以在当前文件夹下新建__init__.py空文件，这样语法检查器会认为这是一个包，可以被导入而不会出现警告。
from .databases import Base


# class Books(Base):
#     __tablename__ = "books"

#     id = Column(Integer, primary_key=True, index=True)
#     bookname = Column(String(100), unique=True)
#     prices = Column(Integer)

class Chat(Base):  # 所有用户的提问和ai的回答都存储在这个表，所以一个人会有多条记录
     __tablename__ = "chat"

     id = Column(Integer, primary_key=True, index=True)
     # 微信 unionid长度29, 一个人会有多条记录所以在这个表里unionid不唯一
     user_unionid = Column(String(29),  index=True)
     nickname = Column(String(50), index=True)        # 微信 昵称
     # true 表示是ai的回答， false表示是用户的提问
     is_answer = Column(Boolean, default=False)

     # gpt-3.5-turbo最大tokens数 4,096； gpt-4-0314最大tokens数 8,192； gpt-4-32k-0314 最大tokens数 32k
     ask_or_answer = Column(String(5200))   # 用户提问或ai回答的具体内容
     datatime = Column(DateTime)


class Context(Base):   # 这个表一个用户只有一条最新的纪录。 gpt-3.5-turbo模型的system assistant，累加存储先前的响应，帮助openai理解上下文
     __tablename__ = "context"

     id = Column(Integer, primary_key=True, index=True)
     user_unionid = Column(String(29), unique=True, index=True)        # 微信 unionid， 长度29
     nickname = Column(String(50), index=True)                    # 微信 昵称

     # gpt-3.5-turbo最大tokens数 4,096； gpt-4-0314最大tokens数 8,192； gpt-4-32k-0314 最大tokens数 32k 
     user_or_assistant = Column(String(1000))            # 所以我们人为设定，累加的assistant最长是1000
     datatime = Column(DateTime)






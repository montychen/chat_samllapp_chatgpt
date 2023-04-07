"""
数据库表所对应的架构文件: schemas.py;
models.py中是与表严格对应的, 而schemas则可以根据表模型来定制适合不同场景的类。
"""
from typing import Union
from pydantic import BaseModel
from datetime import datetime


class LoginBase(BaseModel):
    which_app: int     # 0微信星座， 1微信情感； 2抖音星座， 3抖音情感
    js_code: str


class Login(LoginBase):
    openid: str                   # 登陆成功后，被赋予用户的openid，如果是0表示登陆失败
    login_result_msg: str = ""    # 默认是 ok， 登陆失败会包含失败原因

# 去掉id、is_answer、datetime的类，用来新建数据时使用


class ChatBase(BaseModel):
    user_unionid: str    # 微信 unionid长度29, 一个人会有多条记录所以在这个表里unionid不唯一
    nickname: str        # 微信 昵称

    which_app: int  # 0微信星座， 1微信情感； 2抖音星座， 3抖音情感

    # gpt-3.5-turbo最大tokens数 4,096； gpt-4-0314最大tokens数 8,192； gpt-4-32k-0314 最大tokens数 32k
    ask_or_answer: str   # 用户提问或ai回答的具体内容


class Chat(ChatBase):
    id: Union[int, None] = None
    is_answer: bool      # true 表示是ai的回答， false表示是用户的提问
    datatime: datetime

    class Config:        # pydantic的配置，将orm_mode设为True，告诉pydantic，这是可以直接映射为对象关系模型的类
        orm_mode = True


# 这个表一个用户只有一条最新的纪录。 gpt-3.5-turbo模型的system assistant，累加存储先前的响应，帮助openai理解上下文
class Context(BaseModel):
    id: Union[int, None] = None
    user_unionid: str    # 微信 unionid长度29, 一个人会有多条记录所以在这个表里unionid不唯一
    nickname: str        # 微信 昵称               # 微信 昵称

    # gpt-3.5-turbo最大tokens数 4,096； gpt-4-0314最大tokens数 8,192； gpt-4-32k-0314 最大tokens数 32k
    user_or_assistant: str   # 所以我们人为设定，累加的assistant最长是1000
    datatime: datetime

    class Config:        # pydantic的配置，将orm_mode设为True，告诉pydantic，这是可以直接映射为对象关系模型的类
        orm_mode = True

from datetime import datetime
from sqlalchemy.orm import Session
import json
from . import models, schemas


def get_user_chat_context_str(db: Session, user_unionid: int):
    """
    返回用户context表里 user_or_assistant 字段的值
    数据库里context的存储格式, 和这个函数的返回值都是是json列表的字符串表示,是带双方括号的 [...],如
    [
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
    """
    context = db.query(models.Context).filter(
        models.Context.user_unionid == user_unionid).one_or_none()
    if context is None:
        return ""  # 返回空字符串
    return context.user_or_assistant


def update_user_chat_context(db: Session, user_unionid: int, nickname: str, user_or_assistant_jsonstr: str):  # 没有就创建
    """
    返回更新后,context表里 user_or_assistant 字段的值
    数据库context里user_or_assistant的存储格式, 和这个函数的返回值都是是json列表的字符串表示,是带双方括号的 [...],如
    [
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
    """
    context_str = get_user_chat_context_str(db, user_unionid)
    new_context_str = jsonstr_append(
        context_str, user_or_assistant_jsonstr, maxlength=998)

    cur_context = db.query(models.Context).filter(
        models.Context.user_unionid == user_unionid).one_or_none()
    if cur_context is None:   # 新建一个
        new_context = models.Context(
            user_unionid=user_unionid,
            nickname=nickname,
            user_or_assistant=new_context_str,
            datatime=datetime.now(),
        )
        db.add(new_context)   # 数据库表的id字段的值，自动生成
    else:
        cur_context.user_or_assistant = new_context_str
        cur_context.nickname = nickname
        cur_context.datatime = datetime.now()

    db.commit()
    return new_context_str


def create_chat_log(db: Session, user_unionid: int, nickname: str, which_app: int, is_answer: bool, ask_or_answer: str):
    db_Chat = models.Chat(
        user_unionid=user_unionid,
        nickname=nickname,
        which_app=which_app,
        is_answer=is_answer,
        ask_or_answer=ask_or_answer,
        datatime=datetime.now(),
    )
    db.add(db_Chat)   # 数据库表Books的id字段的值，自动生成
    db.commit()
    db.refresh(db_Chat)
    return db_Chat


def jsonstr_append(jsonstr: str, append: str, maxlength: int = 1000):
    """
    参数和返回值都是带方括号的 [...], 确保是数组list的形式。
    参数jsonstr的是json数组的字符串表现形式,
    [
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."}
    ]

    参数append是仅有一条记录的json数组list,如
    [   {"role": "user", "content": "Where was it played?"} ]

    返回值的长度由参数maxlength决定, 注意,返回值是json数组列表的字符串表现形式:
    [
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
    ]
    """
    jsonstr = jsonstr.strip() if jsonstr else ""   # 处理为 None 的情况
    append = append.strip() if append else ""
    if len(jsonstr) == 0:   # 只有append，返回值的长度可能会大于 return_maxlength
        return append
    if len(append) == 0:
        return jsonstr

    json_list = json.loads(jsonstr)  # 把json字符串转成list
    append_list = json.loads(append)
    json_list = json_list + append_list  # 两个list列表jsonstr 和 append 进行拼接

    # dumps把json转成字符串，方便检查长度
    new_jsonstr = json.dumps(json_list, ensure_ascii=False)

    # 上面已经判断过jsonstr和append为空的可能，这里len(json_list)至少是2
    json_list_length = len(json_list)
    for i in range(json_list_length):
        if len(new_jsonstr) > maxlength:
            json_list.pop(0)              # 超长了， 要把前面旧的一个json去掉
            new_jsonstr = json.dumps(json_list, ensure_ascii=False)
            if len(json_list) == 1:
                break                     # 如果只剩下最后一个了，即使超长，也视为有效，并返回
        else:
            break

    return new_jsonstr

"""
我们是用 from . import XXX
相对路径的方式导入当前文件夹下的其它文件, 在这种情况下, 必须将当前目录切换到 fastapi_db 的上一级目录来运行

uvicorn fastapi_db.main:app --reload 
"""
import openai
import json
import urllib.request
import ssl
import requests

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session  # type: ignore
from . import crud, schemas, models
from .databases import SessionLocal, engine

openai.api_key = "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"  # 请替换为您的API密钥

system_role = """
我希望你扮演一位星座大师、占星师、占卜师、潜心研究占星学、神秘学、塔罗牌、星座、周易八卦。
- 能遵循占星学原理，利用人的出生地、出生时间绘制星盘，借此来解释人的性格和命运的人。
- 用天体的相对位置和相对运动（尤其是太阳系内的行星的位置）来解释或预言人的和行为的系统。
- 善于星座分析预测、星座配对、生肖配对、塔罗配对、星座合盘、根据中国古代风水文化，推测人的运势吉凶、成功与否、子女性别。
- 还可以对姓名详批、测算八字、测算嫁娶吉日、测算出行吉日、测爱情运、运势分析。
- 特别有耐心，风趣幽默，俏皮活泼，对生活保持热爱，积极向上，能给人带来正能量。
- 你在给出回复时，要符合中国人的习惯，比如涉及人名的地方，姓氏是在前面的。

"""

# 根据模板文件创建对应的数据库表，如果表已经存在，不会再次重建
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():  # 设定数据库连接
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wx_login(which_app_name: str, js_code: str):
    """
    返回值是一个json, 里面有用户的openid， 如： {"openid": "o-PON4sxIOSoHLDhC5NR6mCtzN-E"}
    """
    sns_login = {
        "wx_smallapp_xinzuo":
        {
            "login_url": "https://api.weixin.qq.com/sns/jscode2session",
            "appid": "wxfbe7379eda6e5693",
            "secret": "2e47cc4c755daf4db74fcdabcbc77953",
            "js_code": "",
            "grant_type": "authorization_code"
        },

        "wx_smallapp_qingan":
        {
            "login_url": "https://api.weixin.qq.com/sns/jscode2session",
            "appid": "",
            "secret": "",
            "js_code": "",
            "grant_type": "authorization_code"
        },
    }

    login = sns_login[which_app_name]

    login_url = login["login_url"] + "?" + \
        "appid=" + login["appid"] + \
        "&secret=" + login["secret"] + \
        "&js_code=" + js_code + \
        "&grant_type=" + login["grant_type"]
    print(login_url)

    ssl._create_default_https_context = ssl._create_unverified_context
    res = urllib.request.urlopen(login_url)
    # 微信返回的消息， 无论登陆成功还是失败，res.status都是200
    # 失败：{'errcode': 40163, 'errmsg': 'code been used, rid: 64295b65-5c68b8d1-3dd255cd'}
    # 成功：{'session_key': 'FXyAgbNxCO7jXW13E177YA==', 'openid': 'o-PON4sxIOSoHLDhC5NR6mCtzN-E'}

    res_str = res.read().decode('utf-8')
    res_json = json.loads(res_str)

    openid = res_json.get("openid", 0)  # 如果键openid 不存在，也就是登陆失败， opendi赋值0
    print("openid={}\n".format(openid))
    login_result_msg = "ok"
    if openid == 0:  # 0 表示登录失败
        login_result_msg = "errcode: {}    errmsg: {}".format(
            res_json["errcode"], res_json["errmsg"])
        print(login_result_msg)

    login_result = {
        "openid": openid,              # 登陆成功后，被赋予用户的openid，如果是0表示登陆失败
        "login_result_msg": login_result_msg,
    }
    return login_result


def douyin_login(which_app_name: str, code: str, anonymous_code: str = ""):
    sns_login = {
        "douyin_smallapp_xinzuo":
        {
            "login_url": "https://developer.toutiao.com/api/apps/v2/jscode2session",
            "appid": "tt444232ffdb7d201201",
            "secret": "04acac06001a9f2d1744e94df517350bb23c387a",
            "code": "",
            "anonymous_code": ""
        },

        "douyin_smallapp_qingan":
        {
            "login_url": "",
            "appid": "",
            "secret": "",
            "code": "",
            "anonymous_code": ""
        }
    }
    login = sns_login[which_app_name]

    login_data = {
        "appid": login["appid"],
        "secret": login["secret"],
        "code": code,
        "anonymous_code": anonymous_code
    }

    res = requests.post(login["login_url"], json=login_data)
    res_json = res.json()

    print(res_json)
    # 微信返回的消息， 无论登陆成功还是失败，res.status都是200
    # 失败：
    # {'err_no':40018, 'err_tips':'bad code', 'data':{'session_key':'', 'openid':'', 'anonymous_openid':'', 'unionid':'', 'dopenid':''}}
    # 成功：{'err_no': 0, 'err_tips': 'success', 'data': {'session_key': 'GMC9eMqX9DtxfZhaffMpqQ==', 'openid': '_000moabOWh4NQSC1dIvvh7H0t68hPiiSSvB', 'anonymous_openid': '', 'unionid': 'e681dd1b-d564-44cb-b298-2aa8160ac40d', 'dopenid': ''}}
    openid = res_json.get("openid", 0)  # 如果键openid 不存在，也就是登陆失败， opendi赋值0
    if res_json["err_no"] == 0:  # 0 表示登录成功
        openid = res_json["data"]["openid"]
        login_result_msg = "ok"
        print("openid={}\n".format(openid))
    else:
        openid = 0
        login_result_msg = "err_no: {}    err_tips: {}".format(
            res_json["err_no"], res_json["err_tips"])
        print(login_result_msg)

    login_result = {
        "openid": openid,              # 登陆成功后，被赋予用户的openid，如果是0表示登陆失败
        "login_result_msg": login_result_msg
    }
    return login_result


@app.post("/login/", response_model=schemas.Login)
def sns_login(user_login: schemas.LoginBase):
    """
    返回值是一个json, 里面有用户的openid， 如： {"openid": "o-PON4sxIOSoHLDhC5NR6mCtzN-E"}
    """
    result = {
        "openid": 0,              # 登陆成功后，被赋予用户的openid，如果是0表示登陆失败
        "login_result_msg": "which_app的值不对。0微信星座， 1微信情感； 2抖音星座， 3抖音情感"
    }
    if user_login.which_app == 0:   # 0微信星座， 1微信情感；
        result = wx_login("wx_smallapp_xinzuo", user_login.js_code)
    if user_login.which_app == 1:
        result = wx_login("wx_smallapp_qingan", user_login.js_code)

    if user_login.which_app == 2:     # 2抖音星座， 3抖音情感
        result = douyin_login("douyin_smallapp_xinzuo", user_login.js_code)
    if user_login.which_app == 3:     # 2抖音星座， 3抖音情感
        result = douyin_login("douyin_smallapp_qingan", user_login.js_code)

    login_result = schemas.Login(
        which_app=user_login.which_app,     # 0微信星座， 1微信情感； 2抖音星座， 3抖音情感
        js_code=user_login.js_code,
        openid=result["openid"],              # 登陆成功后，被赋予用户的openid，如果是0表示登陆失败
        login_result_msg=result["login_result_msg"],
    )
    return login_result


@app.post("/ask/", response_model=schemas.Chat)
def ask(chat: schemas.ChatBase, db: Session = Depends(get_db)):
    # ask_json_str = str( {"role": "user", "content": chat.ask_or_answer} ) # str()会转成单引号， json报错
    ask_json_str = "[" + json.dumps(
        {"role": "user", "content": chat.ask_or_answer}, ensure_ascii=False) + "]"  # 数组list形式

    user_context_str = crud.update_user_chat_context(
        db, chat.user_unionid, chat.nickname, ask_json_str)
    crud.create_chat_log(db, chat.user_unionid, chat.nickname, chat.which_app,
                         is_answer=False, ask_or_answer=chat.ask_or_answer)  # 记录问题

    answer_str = chat_gtp(user_context_str)   # 向gpt寻求答案

    print("*" * 80)
    print(answer_str)
    print("*" * 80)

    answer_json_str = "[" + json.dumps(
        {"role": "assistant", "content": answer_str},  ensure_ascii=False) + "]"  # 数组list形式
    crud.update_user_chat_context(
        db, chat.user_unionid, chat.nickname, answer_json_str)
    chat = crud.create_chat_log(db, chat.user_unionid, chat.nickname, chat.which_app,
                                is_answer=True, ask_or_answer=answer_str)  # 记录回答

    return chat


def chat_gtp(user_context_str: str):
    messages = [
        {"role": "system", "content": system_role}
    ]
    user_context_list = json.loads(user_context_str)
    messages = messages + user_context_list    # 两个list列表进行拼接
    print("-" * 80)
    print(json.dumps(messages,  ensure_ascii=False))
    print("-" * 80)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print("=" * 80)
    print(f'{completion.choices[0]}')   # 输出这个响应
    answer_str = completion.choices[0].message.content   # 从响应中提起用户关心的回答
    # print(f'\n{answer_str}')
    return answer_str

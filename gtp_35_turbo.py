import os
import openai

openai.api_key = "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"  # 请替换为您的API密钥


def chat_gtp():
    """
    system系统指令: 有助于设置assistant机器回复的行为，比如指定后续用什么角色回复用户的提问。在下面的例子中，assistant被指示为“我是一个和尚...”。
    user用户发言:  通常是用户输入，描述用户要问的内容，也就是prompt
    assistant机器回复: 由于模型对过去的请求没有记忆，默认是不能理解上下文的。 如果用 assistant 存储先前的响应，这样下一次用户再提问时,
    引用了以前的消息时,后台可以自动帮助openai理解上下文。如果对话超过令牌数量的限制，则需要以某种方式缩短它。

    使用gpt-3.5-turbo您必须保留要传递给模型的对话上下文，以生成相关的连贯响应。这就是它的设计方式。如果您的请求超过 4096 个标记，
    您甚至可能需要通过语义搜索或其他方式总结、修剪或提取相关部分来缩短它，但这本身就是一个完整的主题。

    # 一个gpt-3.5-turbo的例子，  通常，对话首先使用系统消息进行格式化，然后是交替的用户和助理消息。
    # https://blog.csdn.net/qq_42837441/article/details/124656422  json数组和字符串相互转

    openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
                ...
                ...
            ]
        )

    """
    messages = [
        {"role": "system", "content": "You’re a kind helpful assistant"}
    ]

    while True:
        user_input = input("== -> 输入你的问题: ")
        if not user_input.strip():   # 如果用户输入为空，退出程序
            break
        messages.append({"role": "user", "content": user_input})

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # print(f'{completion.choices[0]}')   # 输出这个响应
        chat_response = completion.choices[0].message.content   # 从响应中提起用户关心的回答
        print(f'\n{chat_response}')
        # 用 assistant 存储先前的响应，这样下一次问问题的时候就能形成上下文了
        messages.append({"role": "assistant", "content": chat_response})


if __name__ == "__main__":
    chat_gtp()

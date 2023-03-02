import os
from typing import Tuple, Union, List

import openai

from qq_server.default import Defaults
from qq_server.util import color_report, ReportType
from qq_server.express_package import express_package



if 'OPENAI_API_KEY' not in os.environ:
    print('请将 openai token 写入环境变量 OPENAI_API_KEY 中！')
    exit(-1)

openai.api_key = os.environ['OPENAI_API_KEY']

def make_openai_completion_request(question: Union[str, List[dict]], model: str = 'text-davinci-003', temperature: float = 0.7,
                                   max_tokens: int = 1024, top_p: float = 1, frequency_penalty: float = 0, 
                                   presence_penalty: float = 0) -> Tuple[str, bool]:
    try:
        if model == Defaults.chatgpt:
            assert isinstance(question, list)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=question
            )

            answer: str = response['choices'][0]['message']['content']
            return answer.strip(), True

        elif model.startswith(Defaults.davinci_prefix):
            response = openai.Completion.create(
                model=model,
                prompt=question,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            choices = response['choices']
            first_item = choices[0]
            answer: str = first_item['text']
            return answer.strip(), True
    except Exception as e:
        color_report('请求openai时发生错误：', ReportType.Error)
        color_report(e, ReportType.Error)
        color_report('请检查输入字符长度或者服务器的SSL', ReportType.Error)
        return 'openai 工口发生 :(', False

# 预处理：去除不知道为什么出现在开头的停用词
def pre_wash_openai_completion(input: str) -> str:
    if not isinstance(input, str):
        return input
    # 给结尾增加停用词
    end_ch = input[-1]
    if end_ch not in Defaults.stop_words:
        input += '。'
    
    return input

# 后处理：去除不知道为什么出现在开头的停用词
def suf_wash_openai_completion(out: str) -> str:
    index = 0
    while index < len(out) and out[index] in Defaults.stop_words:
        index += 1

    out = out[index:].strip()

    # 去除开头的A: Q:
    out = out.lstrip('A:').lstrip('Q:')

    # 给结尾增加停用词
    if len(out) > 0:
        end_ch = out[-1]
        if end_ch not in Defaults.stop_words:
            out += '。'
        return out

    
    # 如果为空，发一张表情包
    if len(out) == 0:
        # imageUrl = express_package.Casual
        # cq_code = express_package.get_cq_code(imageUrl)
        return ''
    else:
        return out

# 返回结果和状态
def get_openai_completion(question: Union[str, List[dict]], openai_config: dict, max_repeat_times: int = 3) -> Tuple[str, bool]:
    question = pre_wash_openai_completion(question)
    attemp_time = 0

    while attemp_time < max_repeat_times:
        ret, status = make_openai_completion_request(question, **openai_config)
        ret = suf_wash_openai_completion(ret)
        if status:
            return ret, status
        attemp_time += 1
        color_report('openai服务请求出错{}次，正在进行第{}/{}次尝试'.format(
            attemp_time, attemp_time + 1, max_repeat_times))
    warns = '在三次尝试后，openai服务器仍然响应超时，这有极有可能是openai服务器处于繁忙状态'
    return warns, status

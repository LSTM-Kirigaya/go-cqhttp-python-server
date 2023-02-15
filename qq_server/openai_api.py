import openai
import os
from typing import Tuple
from qq_server.util import color_report, ReportType

_stop_words = set([',', '.', '，', '。', '?', '!', '？', '！'])

if 'OPENAI_API_KEY' not in os.environ:
    print('请将 openai token 写入环境变量 OPENAI_API_KEY 中！')
    exit(-1)

openai.api_key = os.environ['OPENAI_API_KEY']

_max_repeat_times = 3

def get_openai_completion(question: str) -> Tuple[str, bool]:
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        choices = response['choices']
        first_item = choices[0]
        answer: str = first_item['text']
        return answer.strip(), True
    except Exception as e:
        return 'openai 工口发生 :(', False

# 去除不知道为什么出现在开头的停用词
def wash_openai_completion(out: str) -> str:
    index = 0
    while index < len(out) and out[index] in _stop_words:
        index += 1
    return out[index:].strip()

# 返回结果和状态
def get_answer(question: str) -> Tuple[str, bool]:
    attemp_time = 0
    while attemp_time < _max_repeat_times:
        ret, status = get_openai_completion(question)
        ret = wash_openai_completion(ret)
        if status:
            return ret, status
        attemp_time += 1
        color_report('openai服务请求出错{}次，正在进行第{}/{}次尝试'.format(
            attemp_time, attemp_time + 1, _max_repeat_times))
    warns = '在三次尝试后，openai服务器仍然响应超时，这有极有可能是openai服务器处于繁忙状态'
    return warns, status
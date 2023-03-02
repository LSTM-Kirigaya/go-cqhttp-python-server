from typing import Dict, Tuple, List
from enum import Enum
from time import time
import re

from colorama import Fore, Style
import psutil
import yaml

from qq_server.type import CqType, CqAt, CqFace, QQMessageBase, ChatgptInputType

class ReportType(Enum):
    Warn = 'warn'
    Info = 'info'
    Error = 'error'
    Debug = 'debug'

def color_report(message: str, type: ReportType = ReportType.Info):
    flag = ''
    if type == ReportType.Warn:
        flag = Fore.YELLOW
    elif type == ReportType.Error:
        flag = Fore.RED
    elif type == ReportType.Info:
        flag = Fore.GREEN
    elif type == ReportType.Debug:
        flag = Fore.BLUE
    tag = '[{}]'.format(type.value)
    print(flag, tag, message, Style.RESET_ALL)


class DictObj:
    def __init__(self, in_dict: dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)

def dict_to_obj(input_dict: Dict) -> object:
    assert(isinstance(input_dict, dict))
    return DictObj(input_dict)

def has_cq_code(message: str):
    return '[CQ:' in message

# 返回的str是剥离了cq后的消息，List是cq字符串组成的
def take_off_cq_code(message: str) -> Tuple[str, List[str]]:
    if has_cq_code(message):
        cq_searches = re.findall("\[.*?\]", message)
        for cq in cq_searches:
            message = message.replace(cq, '')
        return message.strip(), cq_searches
    else:
        return message.strip(), []

# 返回解析得到的cq对象和对象的CqType，方便调用端进行类型标注
def parse_cq_code(cq_code: str) -> Tuple[object, str]:
    info_blocks = cq_code.strip('[').strip(']').split(',')
    type_info = info_blocks[0]
    key_info = info_blocks[1:]
    cq_type = type_info.strip('CQ:')
    cq_payload_dict = {}
    for key_obj in key_info:
        if '=' not in key_obj:
            color_report('检测到CQ消息中的一条没有=作为分割：{}'.format(key_obj), ReportType.Warn)
            continue
        eq_index = key_obj.index('=')
        key = key_obj[:eq_index]
        value = key_obj[eq_index + 1:]
        cq_payload_dict[key] = value
    
    cq_payload = dict_to_obj(cq_payload_dict)
    if cq_type == CqType.At:
        cq_at: CqAt = cq_payload
        try:
            cq_at.qq = int(cq_at.qq)
        except:
            cq_at.qq = -1
    elif cq_type == CqType.Image:
        pass
    elif cq_type == CqType.Face:
        cq_face: CqFace = cq_payload
        cq_face.id = int(cq_face.id)
    
    return cq_payload, cq_type


# 发送 私聊消息
def get_send_private_request(go_host: str, go_port: int, user_id: int, message: str) -> str:
    get_request = "http://{}:{}/send_private_msg?user_id={}&message={}".format(
        go_host, go_port, user_id, message)
    return get_request

# 发送 群聊消息
def get_send_group_request(go_host: str, go_port: int, group_id: int, message: str) -> str:
    get_request = "http://{}:{}/send_group_msg?group_id={}&message={}".format(
            go_host, go_port, group_id, message)
    return get_request

# chatgpt输入
def make_chatgpt_input_item(type: ChatgptInputType, content: str) -> dict:
    return {'role': type, 'content': content}

# 获取当前服务器资源占用情况
def get_server_condition():
    cpu_usage = psutil.cpu_percent(percpu=True)
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage, memory_usage

def read_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        obj = yaml.load(f.read(), Loader=yaml.FullLoader)
    return obj

def write_yaml(path: str, obj: dict):
    with open(path, 'w', encoding='utf-8') as fp:
        yaml.dump(obj, fp, encoding='utf-8', allow_unicode=True)



class MessageSweeper:
    # qq 号到最近一次发送请求时间的映射
    _remove_same_cache: Dict[int, float] = {}
    # 处理每个 message 的信息
    _handle_message_pool: Dict[int, float] = {}
    _clear_cycle = 10
    _clear_count = 0
    _max_survival_time = 600

    def _sweep_message_pool(self):
        pop_message_ids = []
        for message_id, send_time_stamp in self._handle_message_pool.items():
            survival_time = time() - send_time_stamp
            if survival_time >= self._max_survival_time:
                pop_message_ids.append(message_id)
        
        for message_id in pop_message_ids:
            self._handle_message_pool.pop(message_id)

    # 判断当前QQ号的上一次请求是否超时
    def _exceed_time(self, user_id: int) -> bool:
        time_stamp = time()
        if not self._remove_same_cache.__contains__(user_id):
            return False
        last_time_stamp = self._remove_same_cache.__getitem__(user_id)
        return (last_time_stamp - time_stamp) > 20.0

    # 防止同一个ID 短时间内多次触发响应，判断是否要跳过该请求
    # 防止同一个id的message在10分钟之内发起两次以上的请求
    def skip_resquest(self, data_package: QQMessageBase) -> bool:
        try:
            _ = data_package.sender.user_id
        except:
            return False
        self._clear_count += 1
        if self._clear_count % self._clear_cycle == 0:
            self._sweep_message_pool()
            color_report('清理message_pool，现在pool容量：{}'.format(len(self._handle_message_pool)))

        user_id: int = data_package.sender.user_id
        message_id = data_package.message_id

        if message_id in self._handle_message_pool:
            color_report('检测到id为{}的message在10分钟内再次出现，已经自动屏蔽'.format(message_id))
            return True

        self._handle_message_pool[message_id] = time()

        contained = self._remove_same_cache.__contains__(user_id)
        exceed_time = self._exceed_time(user_id)

        if contained and not exceed_time:
            color_report('检测到id为{}的用户短时间内多次发送，跳过该请求'.format(user_id), ReportType.Info)
            return True
        
        self._remove_same_cache.__setitem__(user_id, time())
        return False

    def exit_handle(self, data_package: QQMessageBase):
        try:
            _ = data_package.sender.user_id
        except:
            return 
        user_id: int = data_package.sender.user_id
        if user_id in self._remove_same_cache:
            self._remove_same_cache.pop(user_id)


sweeper = MessageSweeper()
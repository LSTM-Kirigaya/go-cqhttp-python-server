import requests
from typing import List, Tuple, Union, Set
import atexit
from time import time

from qq_server.type import PrivateMessage, GroupMessage, CqType, CqAt
from qq_server.util import take_off_cq_code, parse_cq_code, color_report, ReportType, read_yaml
from qq_server.util import get_send_group_request, get_send_private_request
from qq_server.openai_api import get_openai_completion
from qq_server.express_package import express_package
from qq_server.tip_command import commmand_mananger
from qq_server.talk_pool import TalkPool
from qq_server.default import Defaults


class ServerBot:
    response_user_ids: Set[int] = {}
    response_group_ids: Set[int] = {}
    greet_user_ids: Set[int] = {}
    greet_group_ids: Set[int] = {}

    preset_facts_string: str = ''
    user_id: int = -1
    password: int = -1

    host: Union[str, None] = None
    port: Union[int, None] = None
    go_host: Union[str, None] = None
    go_port: Union[int, None] = None

    openai_config: dict
    openai_max_repeat_times: int
    talk_pool: TalkPool

    def launch(self, go_cqhttp_config_path: str, python_config_path: str):
        obj = read_yaml(go_cqhttp_config_path)
        http_config = obj['servers'][0]['http']
        url = http_config['post'][0]['url']
        go_port = http_config['port']
        go_host = http_config['host']

        account_info = obj['account']
        account = account_info['uin']
        password = account_info['password']

        host, port = url.replace('http://', '').split(':')
        host = str(host)
        port = int(port)
        go_host = str(go_host)
        go_port = int(go_port)

        self.init_account(account, password)
        self.init_host_port(host, port, go_host, go_port)
        self.load_config(python_config_path)

    def load_config(self, path: str):
        obj = read_yaml(path)
        # 注册需要回复的用户
        self.response_user_ids = set(obj.get('response_user_ids', []))
        self.response_group_ids = set(obj.get('response_group_ids', []))

        # 注册特殊事件（上线，下线）打招呼的用户
        self.greet_user_ids = set(obj.get('greet_user_ids', []))
        self.greet_group_ids = set(obj.get('greet_group_ids', []))

        preset_facts: List[str] = obj.get('preset_facts', '')
        self.preset_facts_string = ''.join(preset_facts)
        
        # 对话池
        talk_pool_config = obj.get('talk_pool_config', Defaults.talk_pool_config)
        max_length = int(talk_pool_config.get('max_length', Defaults.talk_pool_config['max_length']))
        memory_path = str(talk_pool_config.get('memory_path', Defaults.talk_pool_config['memory_path']))
        self.talk_pool = TalkPool(max_length, memory_path)

        # 注册意外退出保护记忆
        atexit.register(self.__when_exit)

        # openai 配置
        self.openai_config = obj.get('openai_config', {})
        self.openai_max_repeat_times = self.openai_config.get('max_repeat_times', Defaults.openai_max_repeat_times)
        if 'max_repeat_times' in self.openai_config:
            self.openai_config.pop('max_repeat_times')

        self.__when_enter(self.talk_pool.error_msg)

    
    def init_account(self, user_id: int, password: int):
        self.user_id = user_id
        self.password = password
    
    def init_host_port(self, host: str, port: int, go_host: str, go_port: int):
        self.host = host
        self.port = port
        self.go_host = go_host
        self.go_port = go_port
    

    # 如果有人@我了，我才回复
    def someone_at_me(self, parsed_cq_codes: List[Tuple[object, str]]) -> bool:
        for p_cq_code, cq_type in parsed_cq_codes:
            if cq_type == CqType.At:
                cq_at: CqAt = p_cq_code
                if cq_at.qq == self.user_id:
                    return True
        return False

    def __when_enter(self, memorty_error_msg: str):
        hello_string = 'Tipthereth上线'
        if memorty_error_msg:
            hello_string += '。记忆数据回滚失败，原因：\n' + memorty_error_msg
        else:
            hello_string += '。系统已成功完成记忆回滚。'
        
        self.greet_broadcast(hello_string)

    
    def __when_exit(self):
        bye_string = '由于server发生未知错误，Tipthereth准备下线\n'
        if self.talk_pool.save_memory():
            count = 0
            for item in self.talk_pool.pool:
                if item is not None:
                    count += 1
            
            bye_string += '- 记忆池保存（成功，保存数量：{}）\n'.format(count)
        else:
            bye_string += '- 记忆池保存（失败）\n'

        self.greet_broadcast(bye_string)

    # 广播消息给所有greet用户
    def greet_broadcast(self, message: str):
        for user_id in self.greet_user_ids:
            self.send_private_message(user_id, message)
        
        for group_id in self.greet_group_ids:
            self.send_group_message(group_id, message)

    def __check_send_condition(self):
        go_port = self.go_port
        go_host = self.go_host
        assert go_port, '未获取go_port'
        assert go_host, '未获取go_host'


    def send_private_message(self, user_id: int, message: str):
        message = message.strip()
        if message:
            self.__check_send_condition()
            get_request = get_send_private_request(self.go_host, self.go_port, user_id, message)        
            color_report('发送GET请求: ' + get_request, ReportType.Debug)
            requests.get(get_request)


    def send_group_message(self, group_id: int, message: str):
        message = message.strip()
        if message:
            self.__check_send_condition()
            get_request = get_send_group_request(self.go_host, self.go_port, group_id, message)
            color_report('发送GET请求: ' + get_request, ReportType.Debug)
            requests.get(get_request)


    def handle_private(self, data_package: PrivateMessage):
        user_id = data_package.sender.user_id
        message_id = data_package.message_id
        if user_id not in self.response_user_ids:
            self.send_private_message(user_id, '您不在我的服务对象中 :(')
            color_report('handle_private发送表情包', ReportType.Debug)
            cq_image = express_package.common_cq_code
            self.send_private_message(user_id, cq_image)
            return

        message, cq_codes = take_off_cq_code(data_package.message)

        color_report('准备处理来自qq用户{}的id为{}的message:{}'.format(
            user_id, message_id, message))

        if self.is_tiphereth_command(message):
            # tip command
            res = self.exec_tiphereth_command(message)
            self.send_private_message(user_id, res)

        else:
            # 默认为openai服务
            openai_text_completion, status = self.handle_openai_request(message, data_package)
            res = openai_text_completion
            color_report('openai 给出的答复:' + openai_text_completion, ReportType.Debug)
            self.send_private_message(user_id, res)
            if status is False:
                cq_image = express_package.error_cq_code
                self.send_private_message(user_id, cq_image)



    def handle_group(self, data_package: GroupMessage):
        message, cq_codes = take_off_cq_code(data_package.message)
        parsed_cq_codes = [parse_cq_code(cq_code) for cq_code in cq_codes]
        if self.someone_at_me(parsed_cq_codes):
            # 根据 @我 的id来确定是否做出回答
            user_id = data_package.sender.user_id
            group_id = data_package.group_id
            message_id = data_package.message_id

            if group_id not in self.response_group_ids:
                self.send_group_message(group_id, '该群不在我的服务对象中 :(')
                return

            at_string = '[CQ:at,qq={}]'.format(user_id)
            if user_id not in self.response_user_ids:
                self.send_group_message(group_id, at_string + ' 你不在我的服务对象中 :(')
                color_report('handle_group发送表情包', ReportType.Debug)
                cq_image = express_package.common_cq_code
                self.send_group_message(group_id, cq_image)
                return

            color_report('准备处理来自qq用户{}的id为{}的message:{}'.format(
                user_id, message_id, message))

            if self.is_tiphereth_command(message):
                # tiphereth command
                res = self.exec_tiphereth_command(message)
                self.send_group_message(group_id, res)

            else:
                # 默认为openai服务
                openai_text_completion, status = self.handle_openai_request(message, data_package)
                res = at_string + ' ' + openai_text_completion

                color_report('openai 给出的答复:' + openai_text_completion, ReportType.Debug)
                self.send_group_message(group_id, res)

                if status is False:
                    cq_image = express_package.error_cq_code
                    self.send_group_message(group_id, cq_image)


    # bot 层面的 openai 请求输入处理
    def handle_openai_request(self, message: str, data_package: Union[PrivateMessage, GroupMessage]) -> Tuple[str, bool]:
        """
        @param message 这个message和data_package.message不一样，输入的message必须剥离了cq code
        @param data_package
        @return openai的回复或者不恰当输出的提醒
        """

        if not message:
            return '请输入有效文本', True
        
        # 发起请求
        preset_fact_string = self.preset_facts_string
        context_string = self.talk_pool.get_QA_context()
        questioner_character_string = self.make_questioner_character(data_package)
        questioner_messsage = '{}，{}'.format(questioner_character_string, message)
        
        openai_input = '{}\n{}\n{}'.format(preset_fact_string, context_string, questioner_messsage)

        openai_reply, status = get_openai_completion(
            question=openai_input,
            openai_config=self.openai_config,
            max_repeat_times=self.openai_max_repeat_times
        )
        
        openai_reply, reply_cq_code = take_off_cq_code(openai_reply)
        if openai_reply and status:
            # 加入记忆池
            self.talk_pool.append_talk_item(
                q=message,
                a=openai_reply
            )

        return openai_reply, status

    def is_tiphereth_command(self, message: str) -> bool:
        return message.startswith('tip.command')

    def exec_tiphereth_command(self, message: str) -> str:
        command_blocks: List[str] = message.split()
        color_report(message, ReportType.Debug)
        command_name = command_blocks[0].split('.')[-1]
        args = command_blocks[1:]
        res = commmand_mananger.exec_tip_command(command_name, args)
        return str(res)

    def make_questioner_character(self, data_package: Union[PrivateMessage, GroupMessage]) -> str:
        nickname = data_package.sender.nickname
        return '我是{}，'.format(nickname)


server_bot = ServerBot()
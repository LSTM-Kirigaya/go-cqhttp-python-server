import yaml
from qq_server import PrivateMessage, GroupMessage, CqType, CqAt
from qq_server import take_off_cq_code, parse_cq_code, color_report, ReportType
from qq_server.openai_api import get_answer
from qq_server.express_package import express_package
from qq_server.tip_command import commmand_mananger

import requests
from typing import List, Tuple, Callable
import random

class ServerBot:
    response_user_ids = {}
    response_group_ids = {}
    preset_facts_string = ''
    user_id = -1
    password = -1

    def read_config_yaml(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            obj = yaml.load(f.read(), Loader=yaml.FullLoader)
        
        self.response_user_ids = set(obj['response_user_ids'])
        self.response_group_ids = set(obj['response_group_ids'])
        preset_facts: List[str] = obj['preset_facts']
        self.preset_facts_string = '\n'.join(preset_facts)
    
    def init_account(self, user_id: int, password: int):
        self.user_id = user_id
        self.password = password

    # 如果有人@我了，我才回复
    def someone_at_me(self, parsed_cq_codes: List[Tuple[object, str]]) -> bool:
        for p_cq_code, cq_type in parsed_cq_codes:
            if cq_type == CqType.At:
                cq_at: CqAt = p_cq_code
                if cq_at.qq == self.user_id:
                    return True
        return False


    def send_private_message(self, user_id: int, message: str):
        get_request = "http://127.0.0.1:5700/send_private_msg?user_id={}&message={}".format(user_id, message)
        color_report('发送GET请求: ' + get_request, ReportType.Debug)
        requests.get(get_request)
    
    def send_group_message(self, group_id: int, message: str):
        get_request = "http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(group_id, message)
        color_report('发送GET请求: ' + get_request, ReportType.Debug)
        requests.get(get_request)

    def handle_private(self, data_package: PrivateMessage):
        user_id = data_package.sender.user_id
        message_id = data_package.message_id
        if user_id not in self.response_user_ids:
            self.send_private_message(user_id, '您不在我的服务对象中 :(')
            color_report('handle_private发送表情包', ReportType.Debug)
            cq_image = self.get_image_cq_code(express_package.CommonUrl)
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
            message = self.preset_facts_string + '\n' + message
            openai_text_completion, status = get_answer(message)
            res = openai_text_completion
            color_report('openai 给出的答复:' + openai_text_completion, ReportType.Debug)
            self.send_private_message(user_id, res)
            if status is False:
                cq_image = self.get_image_cq_code(express_package.ErrorUrl)
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
                cq_image = self.get_image_cq_code(express_package.CommonUrl)
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
                message = self.preset_facts_string + '\n' + message
                openai_text_completion, status = get_answer(message)
                res = at_string + ' ' + openai_text_completion
                color_report('openai 给出的答复:' + openai_text_completion, ReportType.Debug)
                self.send_group_message(group_id, res)

                if status is False:
                    cq_image = self.get_image_cq_code(express_package.ErrorUrl)
                    self.send_group_message(group_id, cq_image)

    def is_tiphereth_command(self, message: str) -> bool:
        return message.startswith('tip.command')

    def exec_tiphereth_command(self, message: str) -> str:
        command_blocks: List[str] = message.split()
        color_report(message, ReportType.Debug)
        command_name = command_blocks[0].split('.')[-1]
        args = command_blocks[1:]
        res = commmand_mananger.exec_tip_command(command_name, args)
        return str(res)


    def get_image_cq_code(self, url: str):
        return '[CQ:image,file={}]'.format(url)

server_bot = ServerBot()
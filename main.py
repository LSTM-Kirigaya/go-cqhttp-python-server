from flask import Flask, request
from qq_server import QQMessageBase, PrivateMessage, GroupMessage, MessageType
from qq_server import dict_to_obj, color_report, ReportType, sweeper
from qq_server import server_bot

import yaml
from typing import Tuple

app = Flask(__name__)


def get_host_port() -> Tuple[str, int]:
    with open('./config.yml', 'r', encoding='utf-8') as f:
        obj = yaml.load(f.read(), Loader = yaml.FullLoader)
    url = obj['servers'][0]['http']['post'][0]['url']
    account_info = obj['account']
    account = account_info['uin']
    password = account_info['password']
    server_bot.init_account(account, password)
    host, port = url.replace('http://', '').split(':')
    return str(host), int(port)


@app.route('/', methods=["POST"])
def post_data():
    raw_package: dict = request.get_json()
    if 'message_type' not in raw_package:
        return 'skip'

    data_package: QQMessageBase = dict_to_obj(raw_package)
    message_type = data_package.message_type

    if sweeper.skip_resquest(data_package):
        return 'skip'

    if message_type == MessageType.Private:
        # 私聊信息
        server_bot.handle_private(data_package)

    if message_type == MessageType.Group:
        # 群聊信息
        server_bot.handle_group(data_package)

    sweeper.exit_handle(data_package)

    return 'ok'


if __name__ == '__main__':
    from gevent import pywsgi

    server_bot.read_config_yaml('./server.yaml')
    host, port = get_host_port()
    server = pywsgi.WSGIServer(
        listener=(host, port),
        application=app,
        log=None
    )
    server.serve_forever()
from flask import Flask, request
from qq_server import QQMessageBase, PrivateMessage, GroupMessage, MessageType
from qq_server import dict_to_obj, color_report, ReportType, sweeper
from qq_server import server_bot
from qq_server import Defaults

import yaml
from typing import Tuple

app = Flask(__name__)

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

    go_cqhttp_config = Defaults.go_cqhttp_config
    python_server_config = Defaults.python_server_config

    server_bot.launch(
        go_cqhttp_config_path=go_cqhttp_config,
        python_config_path=python_server_config
    )

    server = pywsgi.WSGIServer(
        listener=(server_bot.host, server_bot.port),
        application=app,
        log=None
    )
    server.serve_forever()
# go-cqhttp-python-server

![](https://img.shields.io/badge/platform-go--cqhttp-orange) ![](https://img.shields.io/badge/python-%3E%3D3.5-green) ![](https://img.shields.io/badge/server-flask-blue)

# 介绍

用于将openai服务或者其他自定义指令接入QQ的python server

---

# 版本

- 应该支持python3.5以上的版本，反正python3.6~3.8都能用。
- Linux CentOS

---
# 启动
克隆该项目后，你需要做的几步：

1. 确保`main.py`和`go-cqhttp`在同一目录下，如下结构：
```
config.yml
data
device.json
go-cqhttp
logs
main.py
qq_server
server.yaml
session.token
```
2. 将openai key注册到环境变量`OPENAI_API_KEY`，确保`os.environ['OPENAI_API_KEY']`不会报错
3. 在`main.py`平级目录创建`server.yaml`，里面写上你允许机器人回答的群号和用户的QQ：
```yaml
response_user_ids:
  - 123

response_group_ids:
  - 111
```
上述的配置会使得机器人只会回答QQ号为123的人的私聊，或者群号为111中的123的@；其他人的@或者私聊它不会回答；其他群的QQ号为123的用户的@它不会回答。

所谓不会回答就是这样一个情况：

![](https://picx.zhimg.com/80/v2-9365e3a1e226dbfd89407fab0f91be8e_1440w.png)

其中发送的表情包可以在`./qq_server/express_package.py`中调整，默认是从CommonLib这个列表中随机一张图出来。

4. 安装所需要的库
```python
pip3 install gevent flask openai
```
5. 开启虚拟终端后运行
```bash
screen -S qqbot-server
python3 main.py
```

玩得愉快！有问题欢迎提issue！
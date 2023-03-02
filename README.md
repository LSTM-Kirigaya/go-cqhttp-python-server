# go-cqhttp-python-server

![](https://img.shields.io/badge/platform-go--cqhttp-orange) ![](https://img.shields.io/badge/python-%3E%3D3.5-green) ![](https://img.shields.io/badge/server-flask-blue)

知乎文章：https://zhuanlan.zhihu.com/p/605791705

# 介绍

用于将openai服务或者其他自定义指令接入QQ的python server，具有如下功能：

- [x] 支持回复权限，让机器人针对指定的人进行回答，其他人的回答不予理睬。
- [x] 支持填入预设事实，来实现AI的人格识别等功能。 
- [x] 优化请求返回逻辑，极大程度避免AI多重回复的问题。
- [x] 支持上下文环境（机器人记忆）
- [ ] 通过访问数据库来避免go-cqhttp消息发送失败。

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

你还可以在`server.yaml`中添加预设事实：
```yaml
preset_facts:
  - "你现在是Tiphereth，锦恢创造的AI助手"
  - "你的本体在位于北京的服务器中"
  - "你最喜欢的食物是奶茶、麻薯"
  - "你喜欢音乐，尤其喜欢交响乐和弛放音乐"
  - "如果有人问你智障问题，完全可以忽略提问者"
```

再次去提问，大概率出现如下的回复：
![](https://pica.zhimg.com/80/v2-b5c475c2d73d4f6358e09e84c60a2d62_1440w.png)

你完全可以添加自己的预设。

4. 安装所需要的库
```python
pip3 install gevent flask openai requests colorama pyyaml psutil
```
5. 测试openai-api：
```bash
# 可能要等个2-10秒
python3 test.py
```
6. 开启虚拟终端后运行
```bash
screen -S qqbot-server
python3 main.py
```

玩得愉快！有问题欢迎提issue！


--- 

# tip指令系统
我还加了一个简单的指令系统：

![](https://picx.zhimg.com/80/v2-c28ff1458fd78c1fce56672c367b93ae_1440w.png)
通过tip.command.XXX就能调用，想要拓展自己的指令只需要在我的项目的`qq_server/tip_command.py`编写函数即可，函数需要满足：
1. 完整的输入参数的类型标注
2. 返回值为字符串或者返回类型自带__str__方法
3. 不能以下划线开头

比如你要实现一个乘法函数，只需要在`qq_server/tip_command.py`中编写：

```python
def multiple(a: int, b: int) -> str:
    return a * b
```

然后重新运行，在QQ聊天框中输入tip.command.multiple 1 2，就会返回2
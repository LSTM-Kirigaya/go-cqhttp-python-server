import abc
from typing import Any


class MessageType:
    Private = 'private'
    Group = 'group'

class QQMessageBase(abc.ABC):
    post_type: str
    message_type: str
    time: int
    self_id: int
    sub_type: str
    font: int
    message_id: int
    user_id: int
    message: str
    raw_message: str

class PrivateSender(abc.ABC):
    age: int
    nickname: str
    sex: str
    user_id: int

class PrivateMessage(QQMessageBase, abc.ABC):
    sender: PrivateSender
    target_id: int

class GroupSender(abc.ABC):
    age: int
    area: str
    card: str
    level: str
    nickname: str
    role: str
    sex: str
    title: str
    user_id: int

class GroupMessage(QQMessageBase, abc.ABC):
    group_id: int
    message_seq: int
    anonymous: Any
    sender: GroupSender

class CqType:
    At = 'at'
    Image = 'image'
    Face = 'face'

class Cq(abc.ABC):
    pass

class CqAt(Cq, abc.ABC):
    qq: int

class CqImage(Cq, abc.ABC):
    file: str
    url: str

class CqFace(Cq, abc.ABC):
    id: int


class TalkItem:
    Q: str
    A: str
    def __init__(self, q: str, a: str) -> None:
        self.Q = q
        self.A = a


class OpenaiConfig:
    max_repeat_times: int
    model: str
    temperature: float
    max_tokens: int        
    top_p: float
    frequency_penalty: float
    presence_penalty: float


class ChatgptInputType:
    System = 'system'
    User = 'user'
    Assistant = 'assistant'
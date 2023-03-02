from typing import List, Union
import os
from time import time

from qq_server.util import read_yaml, write_yaml, color_report, ReportType
from qq_server.default import Defaults


class RawTalkPool:
    pool: List[dict] = []
    cur_index: int = 0

class TalkPool:
    pool: List[dict] = []
    max_length: int = 50
    cur_index = 0
    memory_path: str
    error_msg: str
    last_save_ts: float

    def __init__(self, max_length: int, memory_path: str) -> None:
        self.max_length = max_length
        self.memory_path = memory_path
        self.error_msg = ''
        self.last_save_ts = time()
        self.load_memory(memory_path)

        if len(self.pool) < max_length:
            self.pool.extend([None] * (max_length - len(self.pool)))
        
        assert len(self.pool) == max_length
    

    def set_pool_max_length(self, max_length: int):
        self.max_length = max_length
    

    def append_talk_item(self, q: str, a: str):
        q = q.lstrip('A:').lstrip('Q:')
        a = a.lstrip('A:').lstrip('Q:')
        talk_item = {
            'q': q,
            'a': a
        }
        cur_index = self.cur_index
        self.pool[cur_index] = talk_item
        self.cur_index = (cur_index + 1) % self.max_length
    

    def get_QA_context(self, return_str:bool = True) -> Union[str, List[dict]]:
        valid_talk_items: List[dict] = []
        
        cur_index = self.cur_index
        max_length = self.max_length
        if self.pool[cur_index]:
            for i, _ in enumerate(self.pool):
                talk_item = self.pool[(i + cur_index) % max_length]
                if talk_item:
                    valid_talk_items.append(talk_item)
        else:
            # 说明pool是从0开始计数的
            valid_talk_items.extend(self.pool[:cur_index])

        if not return_str:
            return valid_talk_items
        context = ''
        for item in valid_talk_items:
            q = item.get('q', None)
            a = item.get('a', None)
            if q and a:
                context += 'Q:{}\nA:{}\n'.format(q, a)
        if len(context) > Defaults.context_max_length:
            context = context[len(context) - Defaults.context_max_length:]
        return context

    def __add_error_msg(self, msg: str):
        self.error_msg += msg + '\n'
        color_report(msg, ReportType.Error)


    def __check_memory_pool(self, obj: dict):
        if 'pool' not in obj:
            self.__add_error_msg('记忆池数据丢失，已经重新建立记忆池')       
            obj['pool'] = []


    def __check_memory_cur_index(self, obj: dict):
        if 'cur_index' not in obj:
            self.__add_error_msg('记忆池 cur_index 属性缺失，可能导致上下文恢复异常，先已经重置为0')
            obj['cur_index'] = 0
        else:
            cur_index = obj['cur_index']
            pool = obj.get('pool', [])
            if cur_index < 0 or cur_index >= len(pool):
                self.__add_error_msg('记忆池 cur_index 越界')
                obj['cur_index'] = 0


    def __check_memory_path_and_return(self, path) -> RawTalkPool:
        if not os.path.exists(path):
            return RawTalkPool()
        try:
            obj = read_yaml(path)
            self.__check_memory_pool(obj)
            self.__check_memory_cur_index(obj)
            raw_pool = RawTalkPool()
            raw_pool.cur_index = obj.get('cur_index', 0)
            raw_pool.pool = obj.get('pool', [])
            return raw_pool

        except Exception as e:
            self.__add_error_msg('进行记忆池有效性检查时发生错误：' + e)
            return RawTalkPool()
            

    def load_memory(self, path):
        config = self.__check_memory_path_and_return(path)

        # 这么做考虑到新的 max_length 和老的可能不一样
        self.cur_index = 0
        memory_pool = config.pool
        memory_cur_index = config.cur_index
        pool = []
        cur_max_length = self.max_length
        for i, _ in enumerate(memory_pool):
            # 优先载入最老的数据
            talk_item = memory_pool[(i + memory_cur_index) % len(memory_pool)]
            pool.append(talk_item)

        if cur_max_length < len(pool):
            pool = pool[len(pool) - cur_max_length:]

        self.pool = pool

        if (time() - self.last_save_ts) > Defaults.talk_pool_config['save_time_interval']:
            self.save_memory()
            self.last_save_ts = time()

    def save_memory(self) -> bool:
        try:
            save_path = self.memory_path
            save_dir = os.path.dirname(save_path)
            if save_dir != '.' and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            save_obj = {
                'pool': self.pool,
                'cur_index': self.cur_index
            }

            write_yaml(save_path, save_obj)
            color_report('当前记忆池已经保存至' + save_path, ReportType.Info)
            return True

        except Exception as e:
            color_report('在尝试保存记忆时发生错误，上下文记忆已经丢失，错误：' + e, ReportType.Error)
            return False
'''
Copyright [2023] [许灿标]
license: Apache License, Version 2.0
email: lcctoor@outlook.com
'''

from json import dumps as jsonDumps
from json import loads as jsonLoads
from pathlib import Path
import openai


class Chat():
    '''
    文档: https://pypi.org/project/openai2
    
    获取api_key:
        获取链接1: https://platform.openai.com/account/api-keys
        获取链接2: https://www.baidu.com/s?wd=%E8%8E%B7%E5%8F%96%20openai%20api_key
    '''
    
    def __init__(self, api_key:str, model:str="gpt-3.5-turbo", **kwargs):
        self.api_key = api_key
        self.model = model
        self.messages = []
        self.kwargs = kwargs

    def rollback(self, n=1):
        self.messages[-2*n:] = []
        for x in self.messages[-2:]:
            print(f"[{x['role']}]: {x['content']}")
    
    def request(self, text:str):
        completion = openai.ChatCompletion.create(**{
            'api_key': self.api_key,
            'model': self.model,
            'messages': self.messages + [{"role": "user", "content": text}],
            **self.kwargs
        })
        answer:str = completion.choices[0].message['content']
        self.messages += [
            {"role": "user", "content": text},
            {"role": "assistant", "content": answer}
        ]
        return answer

    async def asy_request(self, text:str):
        completion = await openai.ChatCompletion.acreate(**{
            'api_key': self.api_key,
            'model': self.model,
            'messages': self.messages + [{"role": "user", "content": text}],
            **self.kwargs
        })
        answer:str = completion.choices[0].message['content']
        self.messages += [
            {"role": "user", "content": text},
            {"role": "assistant", "content": answer}
        ]
        return answer
    
    def dump(self, fpath:str):
        ''' 存档 '''
        jt = jsonDumps(self.messages, ensure_ascii=False)
        Path(fpath).write_text(jt, encoding='utf8')
        return True
    
    def load(self, fpath:str):
        ''' 载入存档 '''
        jt = Path(fpath).read_text(encoding='utf8')
        self.messages += jsonLoads(jt)
        return True
    
    def forge(self, messages:list):
        ''' 伪造对话内容 '''
        for num, text in messages:
            if num == 1:
                self.messages.append({"role": "assistant", "content": text})
            elif num == 2:
                self.messages.append({"role": "user", "content": text})
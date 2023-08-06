from __future__ import annotations

__all__ = ['DictModel', 'StringModel', 'Regex', 'ListModel', 'StringListModel']

import re
from typing import Collection, Any, Iterable, Optional
from collections import UserDict, UserList, UserString, deque, ChainMap
from .base import *



class DictModel(UserDict, BaseCollection):
    """Container for dictionaries"""
        
    def init_data(self) -> dict:
        data = self.kwargs
        for item in reversed(self.args):
            if isinstance(item, dict):
                data.update(self.args)
        return data
        
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return '{}({})'.format(
                type(self).__name__,
                ', '.join([f'{k}={v}' if not isinstance(v, str) else f'{k}="{v}"' for k, v in self.data.items() if v])
        )
    def append(self, value: Any):
        self.args.append(value)
        
    def include(self, **kwargs):
        self.data.update(kwargs)
    
    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data.get(item, None)

    def __delitem__(self, key):
        try:
            del self.data[key]
        finally:
            pass

    
class StringModel(UserString, BaseCollection):
    """Container for strings"""
    
    def init_data(self) -> str:
        if len(self.args) > 0:
            data = str(self.args.pop(0))
        else:
            data = str()
        return data
        
        
class ListModel(UserList, BaseCollection):
    """Container for lists"""
    
    def init_data(self) -> list:
        data = list()
        for item in self.args:
            if isinstance(item, (list, set, deque)):
                data.extend([*item])
            else:
                data.append(item)
        return data
    
    def include(self, *args):
        for item in args:
            if isinstance(item, (list, set, deque)):
                self.data.extend(item)
            else:
                self.data.append(item)
    

class StringListModel(ListModel):
    """Container of list of strings"""
    
    def init_data(self) -> list:
        return [str(i) for i in super().init_data()]
    
    def include(self, *args):
        for item in args:
            if isinstance(item, (set, list, deque)):
                self.extend(item)
            else:
                self.append(item)
    
    def append(self, item: str) -> None:
        if item:
            self.data.append(str(item))
        pass
    
    def extend(self, items: Collection[Any]) -> None:
        self.data.extend([str(i) for i in items if i])
        

class Regex(UserString, BaseCollection):
    """Regex class to manipulate strings"""
    def __init__(self, value: str = ""):
        self.initial = value
        super().__init__(self.init_data())
        
    
    def __repr__(self):
        return f'{type(self).__name__}({self.data})'
    
    @classmethod
    def normalize_whitespaces(cls, value: str):
        return ' '.join([i for i in re.split(r'\s+', value) if i]).strip()
    
    @classmethod
    def normalize_final_point(cls, value: str):
        return re.sub(r'\s+\.|\s\.', '.', value)
    
    @classmethod
    def special_join(cls, seq: Iterable[Any], sep: str = " ") -> str:
        return sep.join([str(item) for item in seq if item])
    
    @classmethod
    def split_lines(cls, value: str):
        return [i for i in [cls.normalize_whitespaces(i) for i in re.split(r'\n\r|\n', value)] if i]
    
    @property
    def digits(self):
        return ''.join(re.findall(r'\d', self.initial))
    
    @property
    def words(self):
        return re.split(r'\s+|\s', self.initial)
    
    def init_data(self) -> str:
        return self.initial
    
    def export(self):
        return self.data
    
    def asjson(self):
        return self.export()




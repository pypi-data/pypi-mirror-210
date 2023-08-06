from __future__ import annotations

__all__ = ['BaseDetaModel', 'BaseCollection', 'AbstractDescriptor', 'BaseDataclass', 'BaseEnum', 'SearchDescriptor',
           'AutoDescriptor', 'NumberDescriptor', 'TextAreaDescriptor', 'RangeDescriptor', 'NoFormDescriptor',
           'HiddenDescriptor', 'BaseContext', 'KeyDescriptor', 'ModelKeyDescriptor', 'SelectDescriptor', ]

from enum import Enum
from abc import ABC, abstractmethod
from typing_extensions import Self
from typing import Callable, Optional, Any, ClassVar, get_type_hints, Union
from collections import ChainMap, UserList, UserString, UserDict
from dataclasses import MISSING, dataclass, Field, fields, asdict, astuple
from .functions import *


class BaseEnum(Enum):
    """Enum base model class"""
    
    @classmethod
    def table(cls):
        return cls.__name__
    
    def json(self):
        return self.name
    
    @property
    def key(self):
        return self.name
    
    def __str__(self):
        return self.value
    
    @property
    def display(self):
        return self.value
    
    @classmethod
    def members(cls):
        return cls.__members__.values()
    
    @classmethod
    def option(cls, item: BaseEnum = None, selected: bool = False):
        if not item:
            return '<option></option>'
        return f'<option id="{type(item).__name__}.{item.key}" value="{item.key}" ' \
               f'{"selected" if selected is True else ""}>{item.display}</option>'
    
    @classmethod
    def options(cls, default: str = None):
        if default:
            if isinstance(default, cls):
                default = default.name
        return ''.join([cls.option(), *[cls.option(member, member.key == default) for member in cls.members()]])


@dataclass
class BaseDataclass(ABC):
    PRIVATE_PARAMS: ClassVar[Optional[str]] = None
    PLURAL: ClassVar[Optional[str]] = None
    SINGULAR: ClassVar[Optional[str]] = None
    INITVARS_NAMES: ClassVar[Optional[list[str]]] = None
    INITFIELDS_NAMES: ClassVar[Optional[list[str]]] = None
    FIELDS_NAMES: ClassVar[Optional[list[str]]] = None
    FIELDS: ClassVar[dict[str, Field]] = None
    DESCRIPTORS: ClassVar[dict[str, AbstractDescriptor]] = None
    
    @classmethod
    def class_name(cls):
        return cls.__name__
    
    @classmethod
    def class_setup(cls):
        cls.INITVARS_NAMES = cls.initvars_names()
        cls.INITFIELDS_NAMES = cls.initfields_names()
        cls.FIELDS_NAMES = cls.fields_names()
        cls.FIELDS = cls.fields()
    
    @classmethod
    def descriptors(cls):
        mapping = ChainMap(*[vars(item) for item in [m for m in cls.bases() if issubclass(m, BaseDataclass)]])
        return {key: value for key, value in mapping.items() if isinstance(value, AbstractDescriptor)}
    
    @classmethod
    def singular(cls):
        return cls.SINGULAR or cls.class_name()
    
    @classmethod
    def plural(cls):
        return cls.PLURAL or f'{cls.singular()}s'
    
    def asdict(self):
        return asdict(self)
    
    def astuple(self):
        return astuple(self)
    
    @classmethod
    def all_fields(cls) -> dict[str, Field]:
        return vars(cls)['__dataclass_fields__']
    
    @classmethod
    def init_fields(cls):
        return {key: value for key, value in cls.all_fields().items() if not str(value.type).__contains__('ClassVar')}
    
    @classmethod
    def init_var_fields(cls):
        return {key: value for key, value in cls.all_fields().items() if str(value.type).__contains__('InitVar')}
    
    @classmethod
    def class_var_fields(cls):
        return {key: value for key, value in cls.all_fields().items() if str(value.type).__contains__('ClassVar')}
    
    @classmethod
    def type_hints(cls):
        return get_type_hints(cls)
    
    @classmethod
    def bases(cls):
        return [item for item in cls.mro() if issubclass(item, BaseDataclass)]
    
    @classmethod
    def fields(cls) -> dict[str, Field]:
        return cls.FIELDS or {item.name: item for item in fields(cls)}
    
    @classmethod
    def fields_names(cls):
        return cls.FIELDS_NAMES or cls.fields().keys()
    
    @classmethod
    def filter_fields(cls, data: dict):
        return {k: v for k, v in data.items() if k in cls.fields_names()}
    
    @classmethod
    def create(cls, *args, **kwargs) -> Self:
        try:
            return cls(*args, **kwargs)
        except BaseException as e:
            return cls(*args, **cls.filter_initfields(kwargs))
    
    @classmethod
    def filter_initfields(cls, data: dict):
        return {key: value for key, value in data.items() if key in cls.initfields_names()}
    
    @classmethod
    def initfields_names(cls) -> list[str]:
        return cls.INITFIELDS_NAMES or [*cls.initvars_names(), *cls.fields_names()]
    
    @classmethod
    def initvars_names(cls) -> list[str]:
        return cls.INITVARS_NAMES or list(cls.init_var_fields().keys())


@dataclass
class BaseDetaModel(BaseDataclass):
    TABLE: ClassVar[Optional[str]] = None
    ITEM_NAME: ClassVar[Optional[str]] = None

    @classmethod
    def table(cls):
        return cls.TABLE or cls.class_name()
    
    @classmethod
    def item_name(cls):
        """ITEM_NAME or slug of table name"""
        return cls.ITEM_NAME or slug(cls.table())

    @property
    def get_key(self):
        return getattr(self, 'key', None)
    


class BaseContext(ChainMap):
    pass


class BaseCollection(ABC):
    def __init__(self, *args, **kwargs):
        self.args = [*args]
        self.kwargs = kwargs
        super().__init__(self.init_data())
        assert isinstance(self, (UserString, UserDict, UserList))

    @abstractmethod
    def init_data(self)-> Union[str, dict, list]:
        return NotImplemented


class AbstractDescriptor(ABC):
    FIELD_TYPE: ClassVar[Optional[type]] = None

    def __init__(self, *args, **kwargs):
        self.args = [item for item in args if not item in [None, '']]
        self._default = kwargs.pop('default', MISSING if self.is_required else None)
        self._default_factory: Callable = kwargs.pop('default_factory', MISSING)
        self._label: Callable = kwargs.pop('label', None)
        self.kwargs = kwargs
        
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f'_{name}'
        self.owner: BaseDetaModel = owner
    
    def __set__(self, instance, value):
        if value is None:
            if self.default_factory is not MISSING:
                value = self.default_factory()
        setattr(instance, self.private_name, value)
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self.default
        return getattr(instance, self.private_name)
    
    @property
    def field_type(self):
        return self.FIELD_TYPE or self.owner.fields()[self.public_name].type
    
    def get_default(self):
        if self.default_factory is not MISSING:
            return self.default_factory()
        elif self.default is not MISSING:
            return self.default
        return None
    
    @property
    def is_required(self):
        return 'required' in self.args
    
    @property
    def is_multiple(self):
        return 'multiple' in self.args
    
    @property
    def required(self):
        return 'required' if self.is_required else ''
    
    @property
    def multiple(self):
        return 'multiple' if self.is_multiple else ''
    
    @property
    def default_factory(self) -> Callable:
        return self._default_factory
    
    @property
    def default(self) -> Any:
        if self._default_factory is not MISSING:
            return None
        return self._default

class DescriptorSubclass(ABC):
    """Used for make base subclasses for specific descriptor classes"""


class SearchDescriptor(DescriptorSubclass):
    pass


class AutoDescriptor(DescriptorSubclass):
    pass


class NumberDescriptor(DescriptorSubclass):
    pass


class RangeDescriptor(NumberDescriptor):
    pass


class TextAreaDescriptor(DescriptorSubclass):
    pass


class SelectDescriptor(DescriptorSubclass):
    pass


class NoFormDescriptor(DescriptorSubclass):
    pass


class HiddenDescriptor(DescriptorSubclass):
    pass

class KeyDescriptor(DescriptorSubclass):
    pass
    

class ModelKeyDescriptor(DescriptorSubclass):
    pass
        

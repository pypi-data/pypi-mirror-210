from __future__ import annotations

__all__ = ['BaseDetaModel', 'BaseCollection', 'BaseDescriptor', 'BaseDataclass', 'BaseEnum','BaseContext',
           'Singleton']

from enum import Enum
from abc import ABC, abstractmethod
from functools import cache
from typing_extensions import Self
from typing import Callable, Optional, Any, ClassVar, get_type_hints, Union, get_origin
from collections import ChainMap, UserList, UserString, UserDict
from dataclasses import MISSING, dataclass, Field, fields, asdict, astuple, InitVar
from .functions import *


def isinstance_of_field(obj: Any) -> bool:
    return isinstance(obj, Field)

def is_classvar(field: Field) -> bool:
    return isinstance_of_field(field) and str(field.type).__contains__('ClassVar')

def is_initvar(field: Field) -> bool:
    return isinstance_of_field(field) and str(field.type).__contains__('InitVar')



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
    
    INITVARS_NAMES: ClassVar[tuple[str]] = None
    INITFIELDS_NAMES: ClassVar[tuple[str]] = None
    FIELDS_NAMES: ClassVar[tuple[str]] = None
    FIELDS: ClassVar[dict[str, Field]] = None
    DESCRIPTORS: ClassVar[dict[str, BaseDescriptor]] = None

    @property
    def repr_string(self):
        items = (f"{k}={getattr(self, k)!r}" for k, d in self.repr_descriptors().items())
        return "{}({})".format(type(self).__name__, ", ".join(items))
    
    @classmethod
    @cache
    def class_name(cls):
        return cls.__name__
    
    @classmethod
    def repr_descriptors(cls):
        return {k: v for k, v in cls.descriptors().items() if v.repr == True}
    
    @classmethod
    def class_setup(cls):
        pass
        
    @classmethod
    @cache
    def base_subclass(cls):
        return BaseDataclass
    
    @classmethod
    @cache
    def descriptors(cls) -> dict[str, BaseDescriptor]:
        if not cls.DESCRIPTORS:
            mapping = ChainMap(*[vars(item) for item in cls.bases()])
            cls.DESCRIPTORS = {key: value for key, value in mapping.items() if isinstance(value, BaseDescriptor)}
        return cls.DESCRIPTORS
    
    @classmethod
    @cache
    def singular(cls) -> str:
        return cls.SINGULAR or cls.class_name()
    
    @classmethod
    @cache
    def plural(cls) -> str:
        return cls.PLURAL or f'{cls.singular()}s'
    
    def asdict(self) -> dict[str, Any]:
        return asdict(self)
    
    def astuple(self) -> tuple:
        return astuple(self)
    
    @classmethod
    @cache
    def all_fields(cls) -> dict[str, Field]:
        return vars(cls)['__dataclass_fields__']
    
    @classmethod
    @cache
    def init_fields(cls) -> dict[str, Field]:
        return {key: value for key, value in cls.all_fields().items() if not is_classvar(value)}
    
    @classmethod
    @cache
    def initvar_fields(cls) -> dict[str, Field]:
        return {key: value for key, value in cls.all_fields().items() if is_initvar(value)}
    
    @classmethod
    @cache
    def classvar_fields(cls) -> dict[str, Field]:
        return {key: value for key, value in cls.all_fields().items() if is_classvar(value)}
    
    @classmethod
    @cache
    def type_hints(cls):
        return get_type_hints(cls)
    
    @classmethod
    @cache
    def bases(cls):
        return tuple([item for item in cls.mro() if issubclass(item, cls.base_subclass()) if not item is cls.base_subclass()])
    
    @classmethod
    def fields(cls) -> dict[str, Field]:
        if not cls.FIELDS:
            cls.FIELDS = {item.name: item for item in fields(cls)}
        return cls.FIELDS
    
    @classmethod
    @cache
    def field(cls, name: str) -> Field:
        return cls.fields().get(name, None)
    
    @classmethod
    @cache
    def descriptor(cls, name: str) -> BaseDescriptor:
        return cls.descriptors().get(name, None)
    
    @classmethod
    @cache
    def fields_names(cls) -> tuple[str]:
        if not cls.FIELDS_NAMES:
            cls.FIELDS_NAMES = tuple(cls.fields().keys())
        return cls.FIELDS_NAMES
    
    @classmethod
    def filter_fields(cls, data: dict) -> dict[str, Any]:
        return {k: v for k, v in data.items() if k in cls.fields_names()}
    
    @classmethod
    def create(cls, *args, **kwargs) -> Optional[Self]:
        result = None
        try:
            result = cls(*args, **kwargs)
        except:
            result = cls(*args, **cls.filter_initfields(kwargs))
        finally:
            return result
    
    @classmethod
    def filter_initfields(cls, data: dict) -> dict[str, Any]:
        return {key: value for key, value in data.items() if key in cls.initfields_names()}
    
    @classmethod
    @cache
    def initfields_names(cls) -> tuple[str]:
        if not cls.INITFIELDS_NAMES:
            cls.INITFIELDS_NAMES = tuple([str(item) for item in [*cls.fields_names(), *cls.initvars_names()] if item])
        return cls.INITFIELDS_NAMES
    
    @classmethod
    @cache
    def initvars_names(cls) -> tuple[str]:
        if not cls.INITVARS_NAMES:
            cls.INITVARS_NAMES = tuple(cls.initvar_fields().keys())
        return cls.INITVARS_NAMES



@dataclass
class BaseDetaModel(BaseDataclass):
    TABLE: ClassVar[Optional[str]] = None
    ITEM_NAME: ClassVar[Optional[str]] = None
    
    @classmethod
    def base_subclass(cls):
        return BaseDetaModel

    @classmethod
    def table(cls) -> str:
        return cls.TABLE or cls.class_name()
    
    @classmethod
    def item_name(cls) -> str:
        """ITEM_NAME or slug of table name"""
        return cls.ITEM_NAME or slug(cls.table())

    @property
    def get_key(self) -> str:
        return getattr(self, 'key', None)
    


class BaseContext(ChainMap):
    pass


class BaseCollection(ABC):
    def __init__(self, *args, **kwargs):
        self.args = [*args]
        self.kwargs = kwargs
        super().__init__(self.init_data())
        assert isinstance(self, (UserString, UserDict, UserList, set))

    @abstractmethod
    def init_data(self)-> Union[str, dict, list, set]:
        return NotImplemented


class BaseDescriptor(ABC):
    FIELD_TYPE: ClassVar[Optional[type]] = None
    HTML_TAG: ClassVar[Optional[str]] = None
    INPUT_TYPE: ClassVar[Optional[str]] = None
    FROZEN: ClassVar[Optional[bool]] = None

    def __init__(self, *args, **kwargs):
        self.args: tuple[str] = tuple([str(item) for item in args if all([isinstance(item, str), (item != '')])])
        self._default = kwargs.pop('default', MISSING if self.is_required else None)
        self._default_factory: Callable = kwargs.pop('default_factory', MISSING)
        self._label: Optional[str] = kwargs.pop('label', None)
        self._hash: Optional[bool] = kwargs.pop('hash', None)
        self._compare: bool = kwargs.pop('compare', True)
        self._private: bool = kwargs.pop('private', False)
        self._repr: bool = kwargs.pop('repr', True)
        self._exclude_db: bool = kwargs.pop('exclude_db', False)
        self._exclude_form: bool = kwargs.pop('exclude_form', False)
        self._frozen: bool = kwargs.pop('frozen', False)
        self._html_tag: Optional[str] = kwargs.pop('html_tag', None)
        self._input_type: Optional[str] = kwargs.pop('input_type', None)
        self.extra_kwargs = kwargs
        
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f'_{name}'
        self.owner: BaseDetaModel = owner
    
    def __set__(self, instance, value):
        processed = self.process_value(instance, value)
        parsed = self.parse(processed)
        self.validate(parsed)
        setattr(instance, self.private_name, parsed)
    
    def __get__(self, instance, owner=None):
        if instance is None:
            return self.default
        return getattr(instance, self.private_name)
    
    def frozen_value(self, instance, value):
        return self.default_factory_if_none(getattr(instance, self.private_name, value))
        
    def process_value(self, instance, value):
        if self.frozen:
            return self.frozen_value(instance, value)
        return self.default_factory_if_none(value)
    
    @property
    def owner_name(self):
        return self.owner.__name__
    
    @property
    def html_tag(self):
        return self.HTML_TAG or self._html_tag
    
    @property
    def input_type(self):
        return self.INPUT_TYPE or self._input_type
    
    @property
    def fullname(self):
        return f'{self.owner_name}.{self.public_name}'
    
    def parse(self, value):
        return value
    
    def validate(self, value):
        pass
        
    @property
    def hashed(self) -> Optional[bool]:
        return self._hash
    
    @property
    def compare(self) -> bool:
        return self._compare
    
    @property
    def frozen(self):
        return self.FROZEN or self._frozen
    
    @property
    def private(self) -> bool:
        return self._private
    
    @property
    def repr(self) -> bool:
        return all([self._repr, (not self.private)])
    
    @property
    def exclude_db(self) -> bool:
        return self._exclude_db
    
    @property
    def exclude_form(self) -> bool:
        return self._exclude_form
    
    @property
    def is_input(self):
        return all([not self.exclude_form, not self.is_select, not self.is_textarea])
    
    @property
    def field_type(self):
        return self.FIELD_TYPE or self.owner.init_fields()[self.public_name].type
    
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
    def is_hidden(self):
        return self.input_type == 'hidden'
    
    @property
    def is_range(self):
        return self.input_type == 'range'
    
    @property
    def is_checkbox(self):
        return self.input_type == 'checkbox'
    
    @property
    def is_select(self):
        return self.html_tag == 'select'
    
    @property
    def is_textarea(self):
        return self.html_tag == 'textarea'
    
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
    def default_factory(self) -> Union[Callable, MISSING]:
        return self._default_factory
    
    @property
    def default(self) -> Any:
        if self._default_factory is not MISSING:
            return None
        return self._default
    
    def default_factory_if_none(self, value):
        if any([(value is None), (value == '')]):
            if self.default_factory is not MISSING:
                return self.default_factory()
        return value
    
        
class Singleton(ABC):
    _this = None
    
    @abstractmethod
    def __new__(cls, *args, **kwargs):
        if cls._this is None:
            cls._this = super().__new__(cls, *args, **kwargs)
        return cls._this
    

__all__ = [
        'Undefined',
        'is_empty_map',
        'is_empty_sequence',
        'no_value',
        'is_missing',
        'is_none',
        'is_empty_string',
        'is_undefined',
        'isinstance_of_type',
        'isdataclass_instance',
        'isdataclass_type',
        'isdetamodel',
        'isdetamodel_type',
        'isdetamodel_instance',
        'issearchfield',
        'isdescriptor',
        'isautofield',
        'istextareafield',
        'ishiddenfield',
        'israngefield',
        'isnoformfield',
        'iskeyfield',
        'ismodelkeyfield'
]

from typing import  Any
from dataclasses import is_dataclass, MISSING
from .base import *
from .subdescriptor import *
from .hints import *

Undefined = object()


def is_undefined(value: Any) -> bool:
    return value is Undefined


def is_none(value: Any) -> bool:
    return value is None


def is_missing(value: Any) -> bool:
    return value is MISSING


def isdetamodel(obj: Any) -> bool:
    if isinstance_of_type(obj):
        return issubclass(obj, BaseDetaModel)
    return isinstance(obj, BaseDetaModel)


def is_empty_string(value: Any) -> bool:
    return value == ''


def no_value(value: Any) -> bool:
    return is_none(value) or is_undefined(value) or is_empty_string(value) or is_missing(value) \
        or is_empty_sequence(value) or is_empty_map(value)


def is_empty_sequence(value: Any) -> bool:
    return True if isinstance(value, TupleSequenceTypes) and len(value) == 0 else False


def is_empty_map(value: Any) -> bool:
    return True if isinstance(value, TupleMapTypes) and len(value) == 0 else False


def isinstance_of_type(obj: Any) -> bool:
    return isinstance(obj, type)


def isdataclass_type(obj: Any) -> bool:
    return not isdataclass_instance(obj) and is_dataclass(obj)


def isdetamodel_type(obj: Any) -> bool:
    return isinstance_of_type(obj) and issubclass(obj, BaseDetaModel)


def isdataclass_instance(obj: Any) -> bool:
    return is_dataclass(obj) and not isinstance_of_type(obj)


def isdetamodel_instance(obj: Any) -> bool:
    return not isinstance_of_type(obj) and isinstance(obj, BaseDetaModel)

def isdescriptor(obj: Any) -> bool:
    return isinstance(obj, BaseDescriptor)

def issearchfield(obj: Any) -> bool:
    return isinstance(obj, SearchDescriptor) and isdescriptor(obj)

def isautofield(obj: Any) -> bool:
    return isinstance(obj, AutoDescriptor) and isdescriptor(obj)

def istextareafield(obj: Any) -> bool:
    return isinstance(obj, TextAreaDescriptor) and isdescriptor(obj)


def israngefield(obj: Any) -> bool:
    return isinstance(obj, RangeDescriptor) and isdescriptor(obj)


def isnoformfield(obj: Any) -> bool:
    return isinstance(obj, NoFormDescriptor) and isdescriptor(obj)


def ishiddenfield(obj: Any) -> bool:
    return isinstance(obj, HiddenDescriptor) and isdescriptor(obj)


def iskeyfield(obj: Any) -> bool:
    return isinstance(obj, KeyDescriptor) and isdescriptor(obj)

def ismodelkeyfield(obj: Any) -> bool:
    return isinstance(obj, ModelKeyDescriptor) and isdescriptor(obj)


def isselectfield(obj: Any) -> bool:
    return isinstance(obj, SelectDescriptor) and isdescriptor(obj)
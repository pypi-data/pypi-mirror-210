from __future__ import annotations

__all__ = ['SearchDescriptor', 'AutoDescriptor', 'NumberDescriptor', 'TextAreaDescriptor', 'RangeDescriptor',
           'NoFormDescriptor', 'HiddenDescriptor', 'KeyDescriptor', 'ModelKeyDescriptor', 'SelectDescriptor',
           'StringDescriptor', 'DecimalDescriptor', 'FloatDescriptor', 'IntDescriptor', 'BoolDescriptor',
           'MultipleDescriptor', 'DescriptorSubclass']

from abc import ABC


class DescriptorSubclass(ABC):
    """Used for make base subclasses for specific descriptor classes"""

class StringDescriptor(DescriptorSubclass):
    pass


class DecimalDescriptor(DescriptorSubclass):
    pass


class SearchDescriptor(DescriptorSubclass):
    pass


class AutoDescriptor(DescriptorSubclass):
    pass


class FloatDescriptor(DescriptorSubclass):
    pass


class IntDescriptor(DescriptorSubclass):
    pass


class RangeDescriptor(DescriptorSubclass):
    pass


class NumberDescriptor(DecimalDescriptor, IntDescriptor, RangeDescriptor, FloatDescriptor):
    pass


class MultipleDescriptor(DescriptorSubclass):
    pass


class BoolDescriptor(DescriptorSubclass):
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


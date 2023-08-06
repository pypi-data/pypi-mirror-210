__all__ = ['Descriptor', 'Validator', 'NumberValidator', 'StringValidator', 'DateTimeValidator', 'DateValidator',
           'TextAreaValidator', 'IntValidator', 'FloatValidator', 'SelfKeyValidator', 'DecimalValidator',
           'AutoValidator', 'PasswordValidator', 'BytesValidator', 'AutoUpdateValidator']

import datetime
from decimal import Decimal
from typing import Optional, Callable
from .base import *
from .type_hint import *


class Descriptor(BaseDescriptor):
    
    def parse(self, value):
        return Parser.get(value, self.field_type)

    def validate(self, value):
        if any([value is None, value == '']):
            if self.is_required:
                raise ValueError(f'{self.fullname}: o valor não pode ser nulo.')
        else:
            if not TypeHint(self.field_type).check_type(value):
                raise ValueError(f'{self.fullname}: o tipo de "{value}" ({type(value)}) não corresponde ao esperado ({self.field_type}).')
    

class Validator(Descriptor):
    def __init__(self, *args, **kwargs):
        self._predicate: Optional[Callable] = kwargs.pop('predicate', None)
        super().__init__(*args, **kwargs)
        
    @property
    def predicate(self):
        return self._predicate
        
    def validate(self, value):
        super().validate(value)
        if self.predicate:
            if self.predicate(value) is False:
                raise ValueError(f'{self.fullname}: o predicativo é falso para "{value}".')


    
class DateTimeValidator(Validator):
    FIELD_TYPE = datetime.datetime
    HTML_TAG = 'input'
    INPUT_TYPE = 'datetime-local'
    
    def __init__(self, *args, **kwargs):
        self._min: Optional[float, int, Decimal] = kwargs.pop('min', None)
        self._max: Optional[float, int, Decimal] = kwargs.pop('max', None)
        super().__init__(*args, **kwargs)

    @property
    def min(self):
        return self._min
    
    @property
    def max(self):
        return self._max
    
    def validate(self, value):
        super().validate(value)
        if self.min:
            if self.min > value:
                raise ValueError(f'{self.fullname}: o valor ({value}) é menor que o esperado ({self.min})')
        if self.max:
            if self.max < value:
                raise ValueError(f'{self.fullname}: o valor ({value}) é maior que o esperado ({self.max})')


class DateValidator(DateTimeValidator):
    FIELD_TYPE = datetime.date
    INPUT_TYPE = 'date'


class NumberValidator(DateTimeValidator):
    FIELD_TYPE = None
    INPUT_TYPE = 'number'
    
    def __init__(self, *args, **kwargs):
        self._step: Optional[float, int] = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
    


class IntValidator(NumberValidator):
    FIELD_TYPE = int


class FloatValidator(NumberValidator):
    FIELD_TYPE = float
    
    
class DecimalValidator(NumberValidator):
    FIELD_TYPE = Decimal



class StringValidator(Validator):
    FIELD_TYPE = str
    HTML_TAG = 'input'
    INPUT_TYPE = 'text'

    def __init__(self, *args, **kwargs):
        self._min_len: Optional[int] = kwargs.pop('min_len', None)
        self._max_len: Optional[int] = kwargs.pop('max_len', None)
        super().__init__(*args, **kwargs)
        
    @property
    def min_len(self):
        return self._min_len
    
    @property
    def max_len(self):
        return self._max_len
    
    def validate(self, value):
        super().validate(value)
        if self.min_len:
            if len(value) < self.min_len:
                raise ValueError(f'{self.fullname}: o tamanho do valor "{value}" ({len(value)}) é menor que o esperado ({self.min_len})')
        if self.max_len:
            if len(value) > self.max_len:
                raise ValueError(f'{self.fullname}: o tamanho do valor "{value}" ({len(value)}) é maior que o esperado ({self.max_len})')


class TextAreaValidator(StringValidator):
    HTML_TAG = 'textarea'
    INPUT_TYPE = None
    
    def __init__(self, *args, **kwargs):
        self._height = kwargs.pop('height', '150px')
        super().__init__(*args, **kwargs)
        
    @property
    def height(self):
        return self._height
    
    
class SelfKeyValidator(StringValidator):
    INPUT_TYPE = 'hidden'
    FROZEN = True
    
    
class PasswordValidator(StringValidator):
    FIELD_TYPE = bytes
    INPUT_TYPE = 'password'
    
    

class BytesValidator(PasswordValidator):
    INPUT_TYPE = 'text'
    
    
class AutoValidator(Validator):
    HTML_TAG = None
    INPUT_TYPE = None
    
    def __init__(self, *args, **kwargs):
        self._func: Callable = kwargs.pop('func', None)
        super().__init__(*args, **kwargs)
        
    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)
        if any([value is None, value == '']):
            value = self.func(instance)
        setattr(instance, self.private_name, value)
        
    @property
    def repr(self) -> bool:
        return False
        
    @property
    def func(self):
        return self._func
    
    
class AutoUpdateValidator(AutoValidator):
    
    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)
        setattr(instance, self.private_name, self.func(instance))
    

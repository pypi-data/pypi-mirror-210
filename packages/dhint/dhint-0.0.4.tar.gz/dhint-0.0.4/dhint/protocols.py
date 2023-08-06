__all__ = [
        'ParserProtocol',
        'ValidatorProtocol',
]

from typing import Union, Protocol
from .hints import *


class ParserProtocol(Protocol):
    def __call__(self, value: ParserEntry) -> Union[ParserEntry, ParserResult]:
        ...


class ValidatorProtocol(Protocol):
    def __call__(self, value: GenericType, types: Types) -> GenericType:
        ...


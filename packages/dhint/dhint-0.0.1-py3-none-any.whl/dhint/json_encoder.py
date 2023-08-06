__all__ = [
        'json_dumps',
        'json_parse',
        'json_loads',
        'JsonEncoder'
]

import json
import datetime
from enum import Enum
from dataclasses import asdict
from collections import UserString
from typing import Any
from .types import *
from .collections import *
from .hints import *

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()[:16]
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, bytes):
            return obj.decode(encoding='utf-8')
        elif isinstance(obj, dict):
            return json_parse(obj)
        elif isinstance(obj, (list, tuple)):
            return [json_parse(item) for item in obj]
        elif isinstance(obj, (UserString, Regex, StringModel)):
            return str(obj)
        elif isinstance(obj, (StringListModel, DictModel, ListModel)):
            return json_parse(obj.data)
        elif isdataclass_instance(obj):
            return json_parse(asdict(obj))
        return json.JSONEncoder.default(self, obj)


def json_loads(obj: str) -> Jsonable:
    return json.loads(obj)


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, cls=JsonEncoder, indent=2, ensure_ascii=False)


def json_parse(obj: Any) -> Jsonable:
    return json_loads(json_dumps(obj))


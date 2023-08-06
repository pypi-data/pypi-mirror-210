import json
from typing import Any, Dict, Type, TypeVar

from pydantic import parse_obj_as
from pydantic.json import pydantic_encoder

T = TypeVar('T')


def to_json(pydantic_obj: Any) -> str:
    return json.dumps(
        pydantic_obj,
        default=pydantic_encoder,
        allow_nan=True,
        indent=2,
    )


def to_json_dict(pydantic_obj: Any) -> Dict[str, Any]:
    return json.loads(to_json(pydantic_obj))


def from_json(obj: Any, cls: Type[T]) -> T:
    if isinstance(obj, str):
        obj = json.loads(obj)
    return parse_obj_as(cls, obj)

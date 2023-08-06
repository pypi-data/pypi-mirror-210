from typing import Dict, Mapping, TypeVar

T, U = TypeVar("T"), TypeVar("U")

def omit_none(m: Mapping[T, U]) -> Dict[T, U]:
    return {k: v for k, v in m.items() if v is not None}

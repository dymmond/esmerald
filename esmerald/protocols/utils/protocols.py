from typing import Any, Dict, Protocol, runtime_checkable


# According to https://github.com/python/cpython/blob/main/Lib/dataclasses.py#L1213
# having __dataclass_fields__ is enough to identity a dataclass.
@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: Dict[str, Any]

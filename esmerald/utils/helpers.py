import asyncio
import functools
import sys
import typing
from inspect import isclass
from typing import Any, Awaitable, Callable, TypeVar, Union

import slugify
from typing_extensions import ParamSpec, TypeGuard, get_args, get_origin

if sys.version_info >= (3, 10):
    from types import UnionType

    UNION_TYPES = {UnionType, Union}
else:  # pragma: no cover
    UNION_TYPES = {Union}

P = ParamSpec("P")
T = TypeVar("T")


def is_async_callable(value: Callable[P, T]) -> TypeGuard[Callable[P, Awaitable[T]]]:
    while isinstance(value, functools.partial):
        value = value.func  # type: ignore[unreachable]

    return asyncio.iscoroutinefunction(value) or asyncio.iscoroutinefunction(value.__call__)  # ty


def is_class_and_subclass(value: typing.Any, _type: typing.Any) -> bool:
    original = get_origin(value)
    if not original and not isclass(value):
        return False

    try:
        if original:
            return original and issubclass(original, _type)
        return issubclass(value, _type)
    except TypeError:
        return False


def clean_string(value: str) -> str:
    return slugify.slugify(value, separator="_")


def is_optional_union(annotation: Any) -> bool:
    return get_origin(annotation) in UNION_TYPES and type(None) in get_args(annotation)

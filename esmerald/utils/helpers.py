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
    """Extends `asyncio.iscoroutinefunction()` to additionally detect async
    `partial` objects and class instances with `async def __call__()` defined.

    Args:
        value: Any

    Returns:
        Bool determining if type of `value` is an awaitable.
    """
    while isinstance(value, functools.partial):
        value = value.func  # type: ignore[unreachable]

    return asyncio.iscoroutinefunction(value) or asyncio.iscoroutinefunction(value.__call__)  # ty


def is_class_and_subclass(value: typing.Any, type_: typing.Any) -> bool:
    """Returns `True` if `value` is a a `class` and is a subtyppe of `type_`.

    Args:
        value (Any): The value to check if is a class and subcalss of `type_`.
        type_ (Any): The type used for `issubclass()` of `value`.

    Returns:
        bool
    """
    origin = get_origin(value)
    if not origin and not isclass(value):
        return False

    try:
        if origin:
            return origin and issubclass(origin, type_)
        return issubclass(value, type_)
    except TypeError:
        return False


def clean_string(value: str) -> str:
    """
    Cleans a given value and removes unicode characters.

    Args:
        value (str): The value to be slugified.

    Returns:
        str
    """
    return slugify.slugify(value, separator="_")


def is_optional_union(annotation: Any) -> bool:
    """Given a type annotation determine if the annotation infers an optional
    union.

    Args:
        annotation: A type.

    Returns:
        True for a union, False otherwise.
    """
    return get_origin(annotation) in UNION_TYPES and type(None) in get_args(annotation)

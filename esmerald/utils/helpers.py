import sys
import types
from typing import Any, Callable, Union

import slugify
from lilya._utils import is_class_and_subclass as is_class_and_subclass  # noqa
from lilya.compat import is_async_callable as is_async_callable  # noqa
from typing_extensions import get_args, get_origin

if sys.version_info >= (3, 10):
    from types import UnionType

    UNION_TYPES = {UnionType, Union}
else:  # pragma: no cover
    UNION_TYPES = {Union}


def clean_string(value: str) -> str:
    """
    Cleans the given string by removing any special characters and replacing spaces with underscores.

    Args:
        value (str): The string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    return slugify.slugify(value, separator="_")


def is_optional_union(annotation: Any) -> bool:
    """
    Checks if the given annotation is an optional Union type.

    Args:
        annotation (Any): The annotation to check.

    Returns:
        bool: True if the annotation is an optional Union type, False otherwise.
    """
    return get_origin(annotation) in UNION_TYPES and type(None) in get_args(annotation)


def is_union(annotation: Any) -> bool:
    """
    Checks if the given annotation is a Union type.

    Args:
        annotation (Any): The annotation to check.

    Returns:
        bool: True if the annotation is a Union type, False otherwise.
    """
    return get_origin(annotation) in UNION_TYPES


def make_callable(obj: Any) -> Callable[..., Any]:
    """
    Returns a callable (a function) that, when called, always returns the given object.

    Args:
        obj: Any non-callable object.

    Returns:
        function: A function that returns obj.
    """
    return lambda *args, **kwargs: obj


def is_lambda(fn: Callable[..., Any]) -> bool:
    return isinstance(fn, types.LambdaType) and fn.__name__ == "<lambda>"

from typing import Any

from esmerald import params
from esmerald.utils.helpers import is_class_and_subclass


def is_requires_scheme(param: Any) -> bool:
    """
    Checks if the object is a security scheme.
    """
    return is_class_and_subclass(param, params.Requires)


def is_security_scheme(param: Any) -> bool:
    """
    Checks if the object is a security scheme.
    """
    if not param:
        return False
    return isinstance(param, params.Security)

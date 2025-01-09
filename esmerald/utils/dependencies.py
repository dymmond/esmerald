from typing import Any

from esmerald import params
from esmerald.security.scopes import Scopes
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


def is_security_scope(param: Any) -> bool:
    """
    Checks if the object is a security scope object.
    """
    if not param:
        return False
    return is_class_and_subclass(param, Scopes)


def is_inject(param: Any) -> bool:
    """
    Checks if the object is an Inject.
    """
    from esmerald.injector import Inject

    return isinstance(param, Inject)

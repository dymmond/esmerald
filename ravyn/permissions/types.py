from typing import Type, TypeVar, Union

from ravyn.permissions import BasePermission

PermissionType = TypeVar("PermissionType", bound=BasePermission)
Permission = Union[Type[PermissionType], Type[BasePermission]]

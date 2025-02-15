from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

from lilya.permissions.base import DefinePermission

from esmerald.exceptions import PermissionDenied
from esmerald.utils.helpers import is_async_callable, is_class_and_subclass
from esmerald.utils.sync import AsyncCallable

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.permissions import BasePermission
    from esmerald.requests import Request
    from esmerald.types import APIGateHandler


async def continue_or_raise_permission_exception(
    request: "Request",
    apiview: "APIGateHandler",
    permission: "BasePermission",
) -> None:
    """
    Check if the request has permission to access the API view.
    If not permitted, raise a PermissionDenied exception.
    """
    has_permission: Callable = permission.has_permission

    if not is_async_callable(has_permission):
        if not has_permission(request=request, apiview=apiview):
            permission_denied(
                request,
                message=getattr(permission, "message", None),
            )
    else:
        is_permission = await has_permission(request=request, apiview=apiview)
        if not is_permission:
            permission_denied(
                request,
                message=getattr(permission, "message", None),
            )


def permission_denied(request: "Request", message: Optional[str] = None) -> None:
    """
    If request is not permitted, determine what kind of exception to raise.
    """
    raise PermissionDenied(detail=message, status_code=403)


def is_esmerald_permission(permission: Union["BasePermission", Any]) -> bool:
    """
    Checks if the given permission is an instance or subclass of BasePermission.

    Args:
        permission (Union["BasePermission", Any]): The permission to check.
    Returns:
        bool: True if the permission is an instance or subclass of BasePermission, False otherwise.
    """

    from esmerald.permissions import BasePermission

    return is_class_and_subclass(permission, BasePermission)


def wrap_permission(
    permission: Union[AsyncCallable, DefinePermission, Any],
) -> Union["BasePermission", DefinePermission]:
    """
    Wraps the given permission into a BasePermission instance if it is not already one.
    Or else it will assume its a Lilya permission and wraps it.

    Args:
        permission (Union["BasePermission", Any]): The permission to be wrapped.
    Returns:
        BasePermission: The wrapped permission instance.
    """
    if is_esmerald_permission(permission):
        return cast("BasePermission", AsyncCallable(permission))

    # If its an instance of a DefinePermission, then return it.
    if isinstance(permission, DefinePermission):
        return permission
    return DefinePermission(cast(Any, permission))

from typing import TYPE_CHECKING, Callable, Optional

from esmerald.exceptions import PermissionDenied
from esmerald.utils.helpers import is_async_callable

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.permissions import BasePermission
    from esmerald.requests import Request
    from esmerald.types import APIGateHandler


async def continue_or_raise_permission_exception(
    request: "Request",
    apiview: "APIGateHandler",
    permission: "BasePermission",
) -> None:
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

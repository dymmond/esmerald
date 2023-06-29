from typing import TYPE_CHECKING, List, Optional

from esmerald.exceptions import PermissionDenied

if TYPE_CHECKING:
    from esmerald.permissions import BasePermission
    from esmerald.permissions.types import Permission
    from esmerald.requests import Request
    from esmerald.types import APIGateHandler


def check_permissions(
    request: "Request",
    apiview: "APIGateHandler",
    permissions: List["Permission"],
) -> None:
    """
    Check if the request should be permitted.
    Raises an appropriate exception if the request is not permitted.
    """
    for permission in permissions:
        if not permission().has_permission(request, apiview):
            permission_denied(
                request,
                message=getattr(permission, "message", None),
            )


def continue_or_raise_permission_exception(
    request: "Request",
    apiview: "APIGateHandler",
    permission: "BasePermission",
) -> None:
    if not permission.has_permission(request=request, apiview=apiview):
        permission_denied(
            request,
            message=getattr(permission, "message", None),
        )


def permission_denied(request: "Request", message: Optional[str] = None) -> None:
    """
    If request is not permitted, determine what kind of exception to raise.
    """
    raise PermissionDenied(detail=message, status_code=403)

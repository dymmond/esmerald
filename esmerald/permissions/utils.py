from typing import TYPE_CHECKING, Optional

from esmerald.exceptions import PermissionDenied

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.permissions import BasePermission
    from esmerald.requests import Request
    from esmerald.types import APIGateHandler


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

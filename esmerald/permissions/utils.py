from typing import TYPE_CHECKING, List, Optional  # noqa

from esmerald.exceptions import PermissionDenied  # noqa

if TYPE_CHECKING:
    from esmerald.permissions.types import Permission  # noqa
    from esmerald.requests import Request  # noqa
    from esmerald.types import APIGateHandler  # noqa


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
    permission: "Permission",
):
    if not permission.has_permission(request, apiview):
        permission_denied(
            request,
            message=getattr(permission, "message", None),
        )


def permission_denied(request: "Request", message: Optional[str] = None) -> PermissionDenied:
    """
    If request is not permitted, determine what kind of exception to raise.
    """
    raise PermissionDenied(detail=message, status_code=403)

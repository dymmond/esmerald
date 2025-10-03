from ravyn import BasePermission, Request
from ravyn.types import APIGateHandler


class IsProjectAllowed(BasePermission):
    """
    Permission to validate if has access to a given project
    """

    async def has_permission(self, request: "Request", apiview: "APIGateHandler"):
        allow_project = request.headers.get("allow_access")
        return bool(allow_project)

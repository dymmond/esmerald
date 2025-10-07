from ravyn import Request
from ravyn.permissions.base import BaseAbstractUserPermission
from ravyn.types import APIGateHandler


class IsUserAdmin(BaseAbstractUserPermission):
    """
    Simply check if a user has admin access or not.

    BaseAbstractUserPermission inherits from BasePermission.
    """

    def is_user_authenticated(self, request: "Request") -> bool:
        """
        Logic to check if the user is authenticated
        """
        ...

    def is_user_staff(self, request: "Request") -> bool:
        """
        Logic to check if user is staff
        """
        ...

    def has_permission(self, request: "Request", controller: "APIGateHandler"):
        super().has_permission(request, controller)
        return bool(request.user and self.is_user_staff(request))

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from typing_extensions import Annotated, Doc

from esmerald.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from esmerald.requests import Request
    from esmerald.types import APIGateHandler

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class BaseOperationHolder:  # pragma: no cover
    def __and__(self, other: Any) -> "OperandHolder":
        return OperandHolder(AND, self, other)

    def __or__(self, other: "Any") -> "OperandHolder":
        return OperandHolder(OR, self, other)

    def __rand__(self, other: Any) -> "OperandHolder":
        return OperandHolder(AND, other, self)

    def __ror__(self, other: "BasePermission") -> "OperandHolder":
        return OperandHolder(OR, other, self)

    def __invert__(self) -> "SingleOperand":
        return SingleOperand(NOT, self)


class SingleOperand(BaseOperationHolder):
    def __init__(self, operator_class: Any, op1_class: Any) -> None:
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class OperandHolder(BaseOperationHolder):
    def __init__(self, operator_class: Any, op1_class: Any, op2_class: Any) -> None:
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class AND:
    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        self.op1 = op1
        self.op2 = op2

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        return self.op1.has_permission(request, apiview) and self.op2.has_permission(
            request, apiview
        )


class OR:
    def __init__(self, op1: "BasePermission", op2: "BasePermission") -> None:
        self.op1 = op1
        self.op2 = op2

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        return self.op1.has_permission(request, apiview) or self.op2.has_permission(
            request, apiview
        )


class NOT:
    def __init__(self, op1: "BasePermission") -> None:
        self.op1 = op1

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        return not self.op1.has_permission(request, apiview)


class BasePermissionMetaclass(BaseOperationHolder, type):  # type: ignore[misc,unused-ignore]
    ...


class BasePermission(metaclass=BasePermissionMetaclass):
    """
    `BasePermission` class object. The entry-point for **all** permissions
    used by `Esmerald.

    When creating a permission or a set of permissions for the application,
    those **must** inherit from the `BasePermission` and implement the `has_permission`.

    **Example**

    ```python
    from esmerald import BasePermission, Request
    from esmerald.types import APIGateHandler


    class IsProjectAllowed(BasePermission):
        '''
        Permission to validate if has access to a given project
        '''

        async def has_permission(self, request: "Request", apiview: "APIGateHandler"):
            allow_project = request.headers.get("allow_access")
            return bool(allow_project)
    ```
    """

    def has_permission(
        self,
        request: Annotated[
            "Request",
            Doc(
                """
                The request object being passed through the request.
                """
            ),
        ],
        apiview: Annotated[
            "APIGateHandler",
            Doc(
                """
                A [handler](https://esmerald.dev/routing/handlers/) usually
                corresponding the [level](https://esmerald.dev/application/levels/)
                where the permission is placed.
                """
            ),
        ],
    ) -> bool:
        """
        **Mandatory** functionality and entry-point for verifying
        if the resource is available or not.

        The `has_permission` can be both `sync` and `async` depending
        of the needs of application.

        Returns:
            Boolean indicating if has or not permission to access the specific resource.

        **Example with `async`**

        ```python
        from esmerald import BasePermission, Request
        from esmerald.types import APIGateHandler


        class IsProjectAllowed(BasePermission):
            '''
            Permission to validate if has access to a given project
            '''

            async def has_permission(self, request: "Request", apiview: "APIGateHandler") -> bool:
                allow_project = request.headers.get("allow_access")
                return bool(allow_project)
        ```

        **Example with `sync`**

        ```python
        from esmerald import BasePermission, Request
        from esmerald.types import APIGateHandler


        class IsProjectAllowed(BasePermission):
            '''
            Permission to validate if has access to a given project
            '''

            def has_permission(self, request: "Request", apiview: "APIGateHandler") -> bool:
                allow_project = request.headers.get("allow_access")
                return bool(allow_project)
        ```
        """
        return True


class BaseAbstractUserPermission(BasePermission):
    """
    Abstract Base class for user validation permissions.
    """

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        try:
            return hasattr(request, "user")
        except ImproperlyConfigured:
            return False

    @abstractmethod
    def is_user_authenticated(self, request: "Request") -> bool:
        """
        This method must be overridden by subclasses.

        Args:
            request: A Lilya 'Connection' instance.

        Returns:
            bool: True or False
        """
        raise NotImplementedError("is_user_uthenticated() must be implemented.")

    @abstractmethod
    def is_user_staff(self, request: "Request") -> bool:
        """
        This method must be overridden by subclasses.

        Args:
            request: A Lilya 'Connection' instance.

        Returns:
            bool: True or False
        """
        raise NotImplementedError("is_user_staff() must be implemented.")


class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        return True


class DenyAll(BasePermission):
    """
    Deny all access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        return False


class IsAuthenticated(BaseAbstractUserPermission):
    """
    Allows access only to authenticated users.
    Raises exception if the AuthenticationMiddleware is not in the `middleware` settings.
    """

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        """
        Args:
            request: A Lilya 'Connection' instance.
            apiview: A Esmerald 'APIController' instance or a `APIGateHandler` instance.

        Returns:
            bool: True or False
        """
        super().has_permission(request, apiview)
        return bool(request.user and self.is_user_authenticated(request))


class IsAdminUser(BaseAbstractUserPermission):
    """
    Allows access only to admin users.
    """

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        """
        Args:
            request: A Lilya 'Connection' instance.
            apiview: A Esmerald 'APIController' instance or a `APIGateHandler` instance.

        Returns:
            bool: True or False
        """
        super().has_permission(request, apiview)
        return bool(request.user and self.is_user_staff(request))


class IsAuthenticatedOrReadOnly(BaseAbstractUserPermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(
        self,
        request: "Request",
        apiview: "APIGateHandler",
    ) -> bool:
        """
        Args:
            request: A Lilya 'Connection' instance.
            apiview: A Esmerald 'APIController' instance or a `APIGateHandler` instance.

        Returns:
            bool: True or False
        """
        super().has_permission(request, apiview)
        return bool(
            request.method in SAFE_METHODS or request.user and self.is_user_authenticated(request)
        )

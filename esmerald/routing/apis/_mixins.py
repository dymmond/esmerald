from typing import Any, Callable, List, Union

from typing_extensions import Annotated, Doc

from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.helpers import is_class_and_subclass


class MethodMixin:
    """
    Mixins for method validations.
    """

    http_allowed_methods: Annotated[
        List[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
    ]

    @classmethod
    def is_method_allowed(
        cls,
        name: Annotated[
            str,
            Doc(
                """
                String referring to the http verb (method) being validated.

                Example: `get`, `post`.
                """
            ),
        ],
        base: Annotated[
            Any,
            Doc(
                """
                The base class being checked against.
                Internally, Esmerald checks against the bases of the class
                upon the `__new__` is called.
                """
            ),
        ],
        method: Annotated[
            Callable[..., Any],
            Doc(
                """
                Uusally referred to a [handler](https://esmerald.dev/routing/handlers/)
                being validated.
                """
            ),
        ],
        error_message: Annotated[
            Union[str, None],
            Doc(
                """
                An error message to be displayed upon the error being thrown.
                """
            ),
        ] = None,
    ) -> bool:
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        if name not in dir(base) and isinstance(
            method,
            (HTTPHandler, WebSocketHandler, WebhookHandler),
        ):
            if (
                hasattr(cls, "extra_allowed")
                and cls.extra_allowed is not None
                and name.lower() in cls.extra_allowed
            ):
                return True

            if name.lower() not in cls.http_allowed_methods:
                if error_message is None:
                    error_message = ", ".join(cls.http_allowed_methods)

                raise ImproperlyConfigured(
                    f"{cls.__name__} only allows functions with the name(s) `{error_message}` to be implemented, got `{name.lower()}` instead."
                )
            elif name.lower() != method.__type__.lower():
                raise ImproperlyConfigured(
                    f"The function '{name.lower()}' must implement the '{name.lower()}()' handler, got '{method.__type__.lower()}()' instead."
                )
        return True

    @classmethod
    def is_signature_valid(
        cls,
        name: Annotated[
            str,
            Doc(
                """
                The name of the function
                """
            ),
        ],
        base: Annotated[
            Any,
            Doc(
                """
                The base class being checked against.
                Internally, Esmerald checks against the bases of the class
                upon the `__new__` is called.
                """
            ),
        ],
        method: Annotated[
            Callable[..., Any],
            Doc(
                """
                Uusally referred to a [handler](https://esmerald.dev/routing/handlers/)
                being validated.
                """
            ),
        ],
        signature_type: Annotated[
            Any,
            Doc(
                """
                The annotation being checked against.
                """
            ),
        ],
    ) -> bool:
        """
        Validates if the signature of a given function is of type `signature_type`.
        """
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        if name not in dir(base) and isinstance(
            method,
            (HTTPHandler, WebSocketHandler, WebhookHandler),
        ):
            if (
                not method.handler_signature.return_annotation
                or method.handler_signature.return_annotation is None
            ):
                return True

            if not is_class_and_subclass(
                method.handler_signature.return_annotation, signature_type
            ):
                raise ImproperlyConfigured(
                    f"{cls.__name__} must return type lists, got {type(method.handler_signature.return_annotation)} instead."
                )
        return True

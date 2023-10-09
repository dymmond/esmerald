from typing import Any, Callable, List, Union

from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.helpers import is_class_and_subclass


class MethodMixin:
    """
    Mixins for method validations.
    """

    http_allowed_methods: List[str] = [
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
        name: str,
        base: Any,
        method: Callable[..., Any],
        error_message: Union[str, None] = None,
    ) -> bool:
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        if name not in dir(base) and isinstance(
            method,
            (HTTPHandler, WebSocketHandler, WebhookHandler),
        ):
            if hasattr(cls, "extra_allowed") and cls.extra_allowed is not None and name.lower() in cls.extra_allowed:  # type: ignore[unreachable]
                return True
            if name.lower() not in cls.http_allowed_methods:
                if error_message is None:
                    error_message = ", ".join(cls.http_allowed_methods)

                raise ImproperlyConfigured(
                    f"{cls.__name__} only allows functions with the name(s) `{error_message}` to be implemented, got `{name.lower()}` instead."
                )
            elif name.lower() != method.__class__.__name__.lower():
                raise ImproperlyConfigured(
                    f"The function '{name.lower()}' must implement the '{name.lower()}()' handler, got '{method.__class__.__name__.lower()}()' instead."
                )
        return True

    @classmethod
    def is_signature_valid(
        cls,
        name: str,
        base: Any,
        method: Callable[..., Any],
        signature_type: Any,
    ) -> bool:
        """
        Validates if the signature of a given function is of type `signature_type`.
        """
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        if name not in dir(base) and isinstance(
            method,
            (HTTPHandler, WebSocketHandler, WebhookHandler),
        ):
            if (  # type: ignore
                not method.signature.return_annotation
                or method.signature.return_annotation is None
            ):
                return True

            if not is_class_and_subclass(method.signature.return_annotation, signature_type):
                raise ImproperlyConfigured(
                    f"{cls.__name__} must return type lists, got {type(method.signature.return_annotation)} instead."
                )
        return True

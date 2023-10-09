from typing import Any, Callable, List, Union

from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.apis._metaclasses import SimpleAPIMeta
from esmerald.routing.apis.base import View


class SimpleAPIView(View, metaclass=SimpleAPIMeta):
    """The Esmerald SimpleAPIView class.

    Subclassing this class will create a view using Class Based Views.
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
            if hasattr(cls, "extra_allowed") and name.lower() in cls.extra_allowed:  # type: ignore[unreachable]
                return True
            if name.lower() not in cls.http_allowed_methods:
                raise ImproperlyConfigured(
                    f"{cls.__name__} only allows functions with the name(s) `{error_message}` to be implemented, got `{name.lower()}` instead."
                )
            elif name.lower() != method.__class__.__name__.lower():
                raise ImproperlyConfigured(
                    f"The function '{name.lower()}' must implement the '{name.lower()}()' handler, got '{method.__class__.__name__.lower()}()' instead."
                )
        return True


class APIView(View):
    """The Esmerald APIView class.

    Subclassing this class will create a view using Class Based Views for everyting.
    """

    ...

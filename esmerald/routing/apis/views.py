from typing import Any, Callable, List, Set, Tuple, Type, Union, cast

from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.apis.base import View


class SimpleAPIMeta(type):
    """
    Metaclass responsible for making sure
    only the CRUD objects are allowed.
    """

    def __new__(cls, name: str, bases: Tuple[Type, ...], attrs: Any) -> Any:
        """
        Making sure the `http_allowed_methods` are extended if inheritance happens
        in the subclass.

        The `http_allowed_methods` is the default for each type of generic but to allow
        extra allowed methods, the `extra_allowed` must be added.
        """
        view = super().__new__

        parents = [parent for parent in bases if isinstance(parent, SimpleAPIMeta)]
        if not parents:
            return view(cls, name, bases, attrs)

        simple_view = cast("SimpleAPIView", view(cls, name, bases, attrs))
        filtered_handlers: List[str] = [
            attr
            for attr in dir(simple_view)
            if not attr.startswith("__") and not attr.endswith("__")
        ]

        for base in bases:
            if (
                hasattr(base, "http_allowed_methods")
                and hasattr(base, "__is_generic__")
                and getattr(base, "__is_generic__", False) not in [False, None]
            ):
                simple_view.http_allowed_methods.extend(base.http_allowed_methods)

        if hasattr(simple_view, "extra_allowed"):
            assert isinstance(
                simple_view.extra_allowed, list
            ), "`extra_allowed` must be a list of strings allowed."

            simple_view.http_allowed_methods.extend(simple_view.extra_allowed)

        allowed_methods: Set[str] = {method.lower() for method in simple_view.http_allowed_methods}
        simple_view.http_allowed_methods = list(allowed_methods)
        message = ", ".join(allowed_methods)

        for handler_name in filtered_handlers:
            for base in simple_view.__bases__:
                attribute = getattr(simple_view, handler_name)
                simple_view.is_method_allowed(handler_name, base, attribute, message)

        return simple_view


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
            if name.lower() not in cls.http_allowed_methods:  # type: ignore[unreachable]
                raise ImproperlyConfigured(
                    f"{cls.__name__} only allows functions with the name(s) `{error_message}` to be implemented, got `{name.lower()}` instead."
                )
        return True


class APIView(View):
    """The Esmerald APIView class.

    Subclassing this class will create a view using Class Based Views for everyting.
    """

    ...

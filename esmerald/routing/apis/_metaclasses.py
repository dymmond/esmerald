from typing import TYPE_CHECKING, Any, List, Set, Tuple, Type, cast

if TYPE_CHECKING:
    from esmerald import SimpleAPIView


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

        http_allowed_methods: List[str] = []
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
                http_allowed_methods.extend(base.http_allowed_methods)

        if hasattr(simple_view, "extra_allowed"):
            assert isinstance(
                simple_view.extra_allowed, list
            ), "`extra_allowed` must be a list of strings allowed."

            http_allowed_methods.extend(simple_view.extra_allowed)

        http_allowed_methods.extend(simple_view.http_allowed_methods)

        # Remove any duplicates
        allowed_methods: Set[str] = {method.lower() for method in http_allowed_methods}

        # Reasign the new clean list
        simple_view.http_allowed_methods = list(allowed_methods)
        for handler_name in filtered_handlers:
            for base in simple_view.__bases__:
                attribute = getattr(simple_view, handler_name)
                simple_view.is_method_allowed(handler_name, base, attribute)
        return simple_view
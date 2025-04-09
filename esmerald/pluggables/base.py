from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import isclass
from typing import TYPE_CHECKING, Any, Iterator, Optional, cast

from monkay import load
from typing_extensions import Annotated, Doc

from esmerald.exceptions import ImproperlyConfigured
from esmerald.protocols.extension import ExtensionProtocol

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class Pluggable:
    """
    The `Pluggable` is a wrapper around an Extension to initialize it lazily.

    Read more about the [Pluggables](https://esmerald.dev/pluggables/) and learn how to use them.

    **Example**

    ```python
    from typing import Optional

    from loguru import logger
    from pydantic import BaseModel

    from esmerald import Esmerald, Extension, Pluggable
    from esmerald.types import DictAny


    class PluggableConfig(BaseModel):
        name: str


    class MyExtension(Extension):
        def __init__(
            self,
            app: Optional["Esmerald"] = None,
            config: PluggableConfig = None,
            **kwargs: "DictAny",
        ):
            super().__init__(app, **kwargs)

        def extend(self, config: PluggableConfig) -> None:
            logger.success(f"Successfully passed a config {config.name}")


    my_config = PluggableConfig(name="my extension")

    pluggable = Pluggable(MyExtension, config=my_config)
    # or
    # pluggable = Pluggable("path.to.MyExtension", config=my_config)

    app = Esmerald(routes=[], extensions={"my-extension": pluggable})
    ```
    """

    def __init__(self, cls: type[ExtensionProtocol] | str, **options: Any):
        self.cls_or_string = cls
        self.options = options

    @property
    def cls(self) -> type[ExtensionProtocol]:
        cls_or_string = self.cls_or_string
        if isinstance(cls_or_string, str):
            self.cls_or_string = cls_or_string = load(cls_or_string)
        return cast(type["ExtensionProtocol"], cls_or_string)

    def __iter__(self) -> Iterator:
        iterator = (self.cls, self.options)
        return iter(iterator)

    def __repr__(self) -> str:  # pragma: no cover
        name = self.__class__.__name__
        options = [f"{key}={value!r}" for key, value in self.options.items()]
        args = ", ".join([self.__class__.__name__] + options)
        return f"{name}({args})"


class Extension(ABC, ExtensionProtocol):
    """
    `Extension` object is the one being used to add the logic that will originate
    the `pluggable` in the application.

    The `Extension` **must implement** the `extend` function.

    Read more about the [Extension](https://esmerald.dev/pluggables/#extension) and learn how to use it.

    **Example**

    ```python
    from typing import Optional

    from esmerald import Esmerald, Extension
    from esmerald.types import DictAny


    class MyExtension(Extension):
        def __init__(self, app: Optional["Esmerald"] = None, **kwargs: "DictAny"):
            super().__init__(app)
            self.kwargs = kwargs

        def extend(self, **kwargs: "DictAny") -> None:
            '''
            Function that should always be implemented when extending
            the Extension class or a `NotImplementedError` is raised.
            '''
            # Do something here
    ```
    """

    def __init__(
        self,
        app: Annotated[
            Optional[Esmerald],
            Doc(
                """
                An `Esmerald` application instance or subclasses of Esmerald.
                """
            ),
        ] = None,
        **kwargs: Annotated[
            Any,
            Doc("""Any additional kwargs needed."""),
        ],
    ):
        super().__init__()
        self.app = app

    @abstractmethod
    def extend(self, **kwargs: Any) -> None:
        raise NotImplementedError("Extension must be implemented by the subclasses.")


BaseExtension = Extension


class ExtensionDict(dict[str, Extension]):
    def __init__(self, data: Any = None, *, app: Esmerald):
        super().__init__(data)
        self.app = app
        self.delayed_extend: Optional[dict[str, dict[str, Any]]] = {}
        for k, v in self.items():
            self[k] = v

    def extend(self) -> None:
        while self.delayed_extend:
            key, val = self.delayed_extend.popitem()
            self[key].extend(**val)
        self.delayed_extend = None

    def ensure_extension(self, name: str) -> None:
        """
        For reordering extension initialization

        class MyExtension2(Extension):

            def extend(self, **kwargs: "DictAny") -> None:
                '''
                Function that should always be implemented when extending
                the Extension class or a `NotImplementedError` is raised.
                '''
                self.app.extensions.ensure_extension("foo")
                # Do something here
        ```

        """
        if name not in self:
            raise ValueError(f"Extension does not exist: {name}")
        delayed = self.delayed_extend
        if delayed is None:
            return
        val = delayed.pop(name, None)
        if val is not None:
            self[name].extend(**val)

    def __setitem__(self, name: Any, value: Any) -> None:
        if not isinstance(name, str):
            raise ImproperlyConfigured("Extension names should be in string format.")

        if isinstance(value, str):
            value = Pluggable(value)

        if isinstance(value, Pluggable):
            cls, options = value
            value = cls(app=self.app, **options)
            if self.delayed_extend is None:
                value.extend(**options)
            else:
                self.delayed_extend[name] = options
        elif isclass(value) and issubclass(value, ExtensionProtocol):
            value = value(app=self.app)
            if self.delayed_extend is None:
                value.extend()
            else:
                self.delayed_extend[name] = {}
        elif isinstance(value, ExtensionProtocol):
            if self.delayed_extend is not None:
                raise ImproperlyConfigured(
                    "Cannot pass an initialized extension in extensions parameter."
                )
        else:
            raise ImproperlyConfigured(
                "An extension must subclass from Extension, implement the ExtensionProtocol "
                "as instance or being wrapped in a Pluggable."
            )

        super().__setitem__(name, value)

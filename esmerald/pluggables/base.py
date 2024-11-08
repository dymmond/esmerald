from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterator, Optional

from typing_extensions import Annotated, Doc

from esmerald.exceptions import ImproperlyConfigured
from esmerald.protocols.extension import ExtensionProtocol
from esmerald.utils.helpers import is_class_and_subclass

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class Pluggable:
    """
    The `Pluggable` is used to create an `Esmerald` pluggable from an `Extension`.
    When Esmerald receives pluggables, it hooks them into the system and allows
    the access via anywhere in the application.

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
            self.app = app

        def extend(self, config: PluggableConfig) -> None:
            logger.success(f"Successfully passed a config {config.name}")


    my_config = PluggableConfig(name="my extension")

    pluggable = Pluggable(MyExtension, config=my_config)

    app = Esmerald(routes=[], pluggables={"my-extension": pluggable})
    ```
    """

    def __init__(self, cls: type["Extension"], **options: Any):
        self.cls = cls
        self.options = options

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
            super().__init__(app, **kwargs)
            self.app = app
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
            Optional["Esmerald"],
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
        super().__init__(app, **kwargs)
        self.app = app

    @abstractmethod
    def extend(self, **kwargs: "Any") -> None:
        raise NotImplementedError("plug must be implemented by the subclasses.")


BaseExtension = Extension


class ExtensionDict(dict[str, Extension]):
    def __init__(self, data: Any = None, *, app: "Esmerald"):
        super().__init__(data)
        self.app = app
        for k, v in self.items():
            self[k] = v

    def __setitem__(self, name: Any, value: Any) -> None:
        if not isinstance(name, str):
            raise ImproperlyConfigured("Pluggable names should be in string format.")
        elif isinstance(value, Pluggable):
            cls, options = value
            value = cls(app=self.app, **options)
            value.extend(**options)
        elif isinstance(value, ExtensionProtocol):
            pass
        elif is_class_and_subclass(value, Extension):
            value = value(app=self.app)
            value.extend()
        else:
            raise ImproperlyConfigured(
                "An extension must subclass from esmerald.pluggables.Extension and added to "
                "a Pluggable object"
            )
        super().__setitem__(name, value)

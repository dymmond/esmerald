import sys
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Union,
    cast,
)

from httpx._client import CookieTypes
from lilya.conf.context_vars import set_override_settings
from lilya.testclient import TestClient  # noqa
from pydantic import AnyUrl

from esmerald.applications import Esmerald
from esmerald.conf import settings
from esmerald.conf.global_settings import EsmeraldAPISettings as Settings
from esmerald.contrib.schedulers import SchedulerConfig
from esmerald.encoders import Encoder
from esmerald.openapi.schemas.v3_1_0 import Contact, License, SecurityScheme
from esmerald.utils.crypto import get_random_secret_key

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

P = ParamSpec("P")


if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Literal

    from esmerald.config import (
        CORSConfig,
        CSRFConfig,
        OpenAPIConfig,
        SessionConfig,
        StaticFilesConfig,
    )
    from esmerald.interceptors.types import Interceptor
    from esmerald.permissions.types import Permission
    from esmerald.pluggables import Pluggable
    from esmerald.routing.gateways import WebhookGateway
    from esmerald.types import (
        APIGateHandler,
        Dependencies,
        ExceptionHandlerMap,
        LifeSpanHandler,
        Middleware,
        SettingsType,
        TemplateConfig,
    )


class EsmeraldTestClient(TestClient):  # type: ignore
    app: Esmerald

    def __init__(
        self,
        app: Esmerald,
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        root_path: str = "",
        backend: "Literal['asyncio', 'trio']" = "asyncio",
        backend_options: Optional[Dict[str, Any]] = None,
        cookies: Optional[CookieTypes] = None,
        headers: Dict[str, str] = None,
    ):
        super().__init__(
            app=app,
            base_url=base_url,
            raise_server_exceptions=raise_server_exceptions,
            root_path=root_path,
            backend=backend,
            backend_options=backend_options,
            cookies=cookies,
            headers=headers,
        )

    def __enter__(self, *args: Any, **kwargs: Dict[str, Any]) -> "EsmeraldTestClient":
        return cast("EsmeraldTestClient", super().__enter__(*args, **kwargs))


def create_client(
    routes: Union["APIGateHandler", List["APIGateHandler"]],
    *,
    settings_module: Union[Optional["SettingsType"], Optional[str]] = None,
    debug: Optional[bool] = None,
    app_name: Optional[str] = None,
    title: Optional[str] = None,
    version: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    contact: Optional[Contact] = None,
    terms_of_service: Optional[AnyUrl] = None,
    license: Optional[License] = None,
    security: Optional[List[SecurityScheme]] = None,
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
    secret_key: Optional[str] = get_random_secret_key(),
    allowed_hosts: Optional[List[str]] = None,
    allow_origins: Optional[List[str]] = None,
    base_url: str = "http://testserver",
    backend: "Literal['asyncio', 'trio']" = "asyncio",
    backend_options: Optional[Dict[str, Any]] = None,
    interceptors: Optional[List["Interceptor"]] = None,
    pluggables: Optional[Dict[str, "Pluggable"]] = None,
    permissions: Optional[List["Permission"]] = None,
    dependencies: Optional["Dependencies"] = None,
    middleware: Optional[List["Middleware"]] = None,
    csrf_config: Optional["CSRFConfig"] = None,
    exception_handlers: Optional["ExceptionHandlerMap"] = None,
    openapi_config: Optional["OpenAPIConfig"] = None,
    on_shutdown: Optional[List["LifeSpanHandler"]] = None,
    on_startup: Optional[List["LifeSpanHandler"]] = None,
    cors_config: Optional["CORSConfig"] = None,
    session_config: Optional["SessionConfig"] = None,
    scheduler_config: Optional[SchedulerConfig] = None,
    enable_scheduler: bool = None,
    enable_openapi: bool = True,
    include_in_schema: bool = True,
    openapi_version: Optional[str] = "3.1.0",
    raise_server_exceptions: bool = True,
    root_path: str = "",
    static_files_config: Optional["StaticFilesConfig"] = None,
    template_config: Optional["TemplateConfig"] = None,
    lifespan: Optional[Callable[["Esmerald"], "AsyncContextManager"]] = None,
    cookies: Optional[CookieTypes] = None,
    redirect_slashes: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    webhooks: Optional[Sequence["WebhookGateway"]] = None,
    encoders: Optional[Sequence[Encoder]] = None,
) -> EsmeraldTestClient:
    return EsmeraldTestClient(
        app=Esmerald(
            settings_module=settings_module,
            debug=debug,
            title=title,
            version=version,
            summary=summary,
            description=description,
            contact=contact,
            terms_of_service=terms_of_service,
            license=license,
            security=security,
            servers=servers,
            routes=cast("Any", routes if isinstance(routes, list) else [routes]),
            app_name=app_name,
            secret_key=secret_key,
            allowed_hosts=allowed_hosts,
            allow_origins=allow_origins,
            interceptors=interceptors,
            permissions=permissions,
            dependencies=dependencies,
            middleware=middleware,
            csrf_config=csrf_config,
            exception_handlers=exception_handlers,
            openapi_config=openapi_config,
            on_shutdown=on_shutdown,
            on_startup=on_startup,
            cors_config=cors_config,
            scheduler_config=scheduler_config,
            enable_scheduler=enable_scheduler,
            static_files_config=static_files_config,
            template_config=template_config,
            session_config=session_config,
            lifespan=lifespan,
            redirect_slashes=redirect_slashes,
            enable_openapi=enable_openapi,
            openapi_version=openapi_version,
            include_in_schema=include_in_schema,
            tags=tags,
            webhooks=webhooks,
            pluggables=pluggables,
            encoders=encoders,
        ),
        base_url=base_url,
        backend=backend,
        backend_options=backend_options,
        root_path=root_path,
        raise_server_exceptions=raise_server_exceptions,
        cookies=cookies,
    )


class override_settings:
    """
    A context manager that allows overriding Esmerald settings temporarily.

    Usage:
    ```
    with override_settings(SETTING_NAME=value):
        # code that uses the overridden settings
    ```

    The `override_settings` class can also be used as a decorator.

    Usage:
    ```
    @override_settings(SETTING_NAME=value)
    def test_function():
        # code that uses the overridden settings
    ```
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the class with the given keyword arguments.

        Args:
            **kwargs: Additional keyword arguments to be stored as options.

        Returns:
            None
        """
        self.app = kwargs.pop("app", None)
        self.options = kwargs

    def __enter__(self) -> None:
        """
        Enter the context manager and set the modified settings.

        Saves the original settings and sets the modified settings
        based on the provided options.

        Returns:
            None
        """
        self._original_settings = settings._wrapped
        settings._wrapped = Settings(settings._wrapped, **self.options)  # type: ignore
        set_override_settings(True)

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """
        Restores the original settings and sets them up again.

        Args:
            exc_type (Any): The type of the exception raised, if any.
            exc_value (Any): The exception instance raised, if any.
            traceback (Any): The traceback for the exception raised, if any.
        """
        settings._wrapped = self._original_settings
        settings._setup()
        set_override_settings(False)

    def __call__(self, test_func: Any) -> Any:
        """
        Decorator that wraps a test function and executes it within a context manager.

        Args:
            test_func (Any): The test function to be wrapped.

        Returns:
            Any: The result of the test function.

        """

        @wraps(test_func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> Any:
            with self:
                return test_func(*args, **kwargs)

        return inner

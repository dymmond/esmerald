from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union, cast

from esmerald.applications import Esmerald
from esmerald.conf import settings
from esmerald.utils.crypto import get_random_secret_key
from starlette.testclient import TestClient as TestClient  # noqa

if TYPE_CHECKING:
    from esmerald.config import (
        CORSConfig,
        CSRFConfig,
        OpenAPIConfig,
        SessionConfig,
        StaticFilesConfig,
        TemplateConfig,
    )
    from esmerald.permissions.types import Permission
    from esmerald.types import (
        APIGateHandler,
        Dependencies,
        ExceptionHandlers,
        LifeSpanHandler,
        Middleware,
        SchedulerType,
    )
    from typing_extensions import Literal


class EsmeraldTestClient(TestClient):
    app: Esmerald

    def __init__(
        self,
        app: Esmerald,
        base_url: str = "http://testserver",
        raise_server_exception: bool = True,
        root_path: str = "",
        backend: "Literal['asyncio', 'trio']" = "asyncio",
        backend_options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            app, base_url, raise_server_exception, root_path, backend, backend_options
        )
        """A reimplementation of the base client of Starlette
        """

    def __enter__(self, *args: Any, **kwargs: Dict[str, Any]) -> "EsmeraldTestClient":
        """The TestClient returned if a EsmeraldTestClient and not a Starlette TestClient."""
        return super().__enter__(*args, **kwargs)


def create_client(
    routes: Union["APIGateHandler", List["APIGateHandler"]],
    *,
    debug: bool = settings.debug,
    name: Optional[str] = settings.app_name,
    secret: Optional[str] = get_random_secret_key(),
    allowed_hosts: Optional[List[str]] = settings.allowed_hosts,
    allow_origins: Optional[List[str]] = settings.allow_origins,
    base_url: str = "http://testserver",
    backend: "Literal['asyncio', 'trio']" = "asyncio",
    backend_options: Optional[Dict[str, Any]] = None,
    permissions: Optional[List["Permission"]] = settings.permissions,
    dependencies: Optional["Dependencies"] = settings.dependencies,
    middleware: Optional[List["Middleware"]] = settings.middleware,
    csrf_config: Optional["CSRFConfig"] = settings.csrf_config,
    exception_handlers: Optional["ExceptionHandlers"] = settings.exception_handlers,
    openapi_config: Optional["OpenAPIConfig"] = settings.openapi_config,
    on_shutdown: Optional[List["LifeSpanHandler"]] = settings.on_shutdown,
    on_startup: Optional[List["LifeSpanHandler"]] = settings.on_startup,
    cors_config: Optional["CORSConfig"] = settings.cors_config,
    session_config: Optional["SessionConfig"] = settings.session_config,
    scheduler_class: Optional["SchedulerType"] = settings.scheduler_class,
    raise_server_exceptions: bool = True,
    root_path: str = "",
    static_files_config: Optional[Union["StaticFilesConfig", List["StaticFilesConfig"]]] = None,
    template_config: Optional["TemplateConfig"] = None,
) -> EsmeraldTestClient:
    """
    Creates a default EsmeraldTestClient to be used in the tests.
    """
    return TestClient(
        app=Esmerald(
            debug=debug,
            routes=cast("Any", routes if isinstance(routes, list) else [routes]),
            name=name,
            secret=secret,
            allowed_hosts=allowed_hosts,
            allow_origins=allow_origins,
            permissions=permissions,
            dependencies=dependencies,
            middleware=middleware,
            csrf_config=csrf_config,
            exception_handlers=exception_handlers,
            openapi_config=openapi_config,
            on_shutdown=on_shutdown,
            on_startup=on_startup,
            cors_config=cors_config,
            scheduler_class=scheduler_class,
            static_files_config=static_files_config,
            template_config=template_config,
            session_config=session_config,
        ),
        base_url=base_url,
        backend=backend,
        backend_options=backend_options,
        root_path=root_path,
        raise_server_exceptions=raise_server_exceptions,
    )

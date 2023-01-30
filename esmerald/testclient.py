from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    cast,
)

import httpx  # noqa
from starlette.testclient import TestClient  # noqa

from esmerald.applications import Esmerald
from esmerald.conf import settings  # noqa
from esmerald.utils.crypto import get_random_secret_key

if TYPE_CHECKING:
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
    from esmerald.types import (
        APIGateHandler,
        Dependencies,
        DictStr,
        ExceptionHandlers,
        LifeSpanHandler,
        Middleware,
        SchedulerType,
        SettingsType,
        TemplateConfig,
    )


class EsmeraldTestClient(TestClient):
    app: Esmerald

    def __init__(
        self,
        app: Esmerald,
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        root_path: str = "",
        backend: "Literal['asyncio', 'trio']" = "asyncio",
        backend_options: Optional[Dict[str, Any]] = None,
        cookies: Optional[httpx._client.CookieTypes] = None,
        headers: Optional["DictStr"] = None,
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
        return super().__enter__(*args, **kwargs)


def create_client(
    routes: Union["APIGateHandler", List["APIGateHandler"]],
    *,
    settings_config: Optional["SettingsType"] = None,
    debug: Optional[bool] = None,
    app_name: Optional[str] = None,
    secret_key: Optional[str] = get_random_secret_key(),
    allowed_hosts: Optional[List[str]] = None,
    allow_origins: Optional[List[str]] = None,
    base_url: str = "http://testserver",
    backend: "Literal['asyncio', 'trio']" = "asyncio",
    backend_options: Optional[Dict[str, Any]] = None,
    interceptors: Optional[List["Interceptor"]] = None,
    permissions: Optional[List["Permission"]] = None,
    dependencies: Optional["Dependencies"] = None,
    middleware: Optional[List["Middleware"]] = None,
    csrf_config: Optional["CSRFConfig"] = None,
    exception_handlers: Optional["ExceptionHandlers"] = None,
    openapi_config: Optional["OpenAPIConfig"] = None,
    on_shutdown: Optional[List["LifeSpanHandler"]] = None,
    on_startup: Optional[List["LifeSpanHandler"]] = None,
    cors_config: Optional["CORSConfig"] = None,
    session_config: Optional["SessionConfig"] = None,
    scheduler_class: Optional["SchedulerType"] = None,
    scheduler_tasks: Optional[Dict[str, str]] = None,
    scheduler_configurations: Optional[Dict[str, Union[str, Dict[str, str]]]] = None,
    enable_scheduler: bool = None,
    raise_server_exceptions: bool = True,
    root_path: Optional[str] = "",
    static_files_config: Optional[Union["StaticFilesConfig", List["StaticFilesConfig"]]] = None,
    template_config: Optional["TemplateConfig"] = None,
    lifespan: Optional[Callable[["Esmerald"], "AsyncContextManager"]] = None,
    cookies: Optional[httpx._client.CookieTypes] = None,
    redirect_slashes: Optional[bool] = None,
) -> EsmeraldTestClient:
    return EsmeraldTestClient(
        app=Esmerald(
            settings_config=settings_config,
            debug=debug,
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
            scheduler_class=scheduler_class,
            scheduler_tasks=scheduler_tasks,
            scheduler_configurations=scheduler_configurations,
            enable_scheduler=enable_scheduler,
            static_files_config=static_files_config,
            template_config=template_config,
            session_config=session_config,
            lifespan=lifespan,
            redirect_slashes=redirect_slashes,
        ),
        base_url=base_url,
        backend=backend,
        backend_options=backend_options,
        root_path=root_path,
        raise_server_exceptions=raise_server_exceptions,
        cookies=cookies,
    )

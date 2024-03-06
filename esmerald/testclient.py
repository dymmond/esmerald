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
from lilya.testclient import TestClient  # noqa
from openapi_schemas_pydantic.v3_1_0 import Contact, License, SecurityScheme
from pydantic import AnyUrl

from esmerald.applications import Esmerald
from esmerald.utils.crypto import get_random_secret_key

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
    settings_config: Optional["SettingsType"] = None,
    settings_module: Optional["SettingsType"] = None,
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
    scheduler_class: Optional["SchedulerType"] = None,
    scheduler_tasks: Optional[Dict[str, str]] = None,
    scheduler_configurations: Optional[Dict[str, Union[str, Dict[str, str]]]] = None,
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
) -> EsmeraldTestClient:
    return EsmeraldTestClient(
        app=Esmerald(
            settings_config=settings_config,
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
            scheduler_class=scheduler_class,
            scheduler_tasks=scheduler_tasks,
            scheduler_configurations=scheduler_configurations,
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
        ),
        base_url=base_url,
        backend=backend,
        backend_options=backend_options,
        root_path=root_path,
        raise_server_exceptions=raise_server_exceptions,
        cookies=cookies,
    )

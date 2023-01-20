from datetime import timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from openapi_schemas_pydantic.v3_1_0 import License, SecurityRequirement, Server
from pydantic import BaseConfig, BaseSettings

from esmerald.config import (
    AsyncExitConfig,
    CORSConfig,
    CSRFConfig,
    OpenAPIConfig,
    SessionConfig,
    StaticFilesConfig,
    TemplateConfig,
)
from esmerald.interceptors.types import Interceptor
from esmerald.permissions.types import Permission
from esmerald.types import (
    APIGateHandler,
    Dependencies,
    ExceptionHandlers,
    LifeSpanHandler,
    Middleware,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
    SchedulerType,
)

# if TYPE_CHECKING:


class AppConfig(BaseSettings):
    """
    Configuration initially used to help and populate the values of an Esmerald
    instance.
    """

    debug: Optional[bool]
    app_name: Optional[str]
    title: Optional[str]
    version: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    contact: Optional[Dict[str, Union[str, Any]]]
    terms_of_service: Optional[str]
    license: Optional[License]
    security: Optional[List[SecurityRequirement]]
    servers: Optional[List[Server]]
    secret_key: Optional[str]
    allowed_hosts: Optional[List[str]]
    allow_origins: Optional[List[str]]
    permissions: Optional[List["Permission"]]
    interceptors: Optional[List["Interceptor"]]
    dependencies: Optional["Dependencies"]
    csrf_config: Optional[Union["CSRFConfig", Any]]
    cors_config: Optional[Union["CORSConfig", Any]]
    openapi_config: Optional[Union["OpenAPIConfig", Any]]
    static_files_config: Optional[Union["StaticFilesConfig", Any]]
    template_config: Optional[Union["TemplateConfig", Any]]
    session_config: Optional[Union["SessionConfig", Any]]
    response_class: Optional["ResponseType"]
    response_cookies: Optional["ResponseCookies"]
    response_headers: Optional["ResponseHeaders"]
    scheduler_class: Optional[Union["SchedulerType", Any]]
    scheduler_tasks: Optional[Dict[Any, Any]]
    scheduler_configurations: Optional[Dict[str, Union[str, Dict[Any, Any]]]]
    enable_scheduler: Optional[bool]
    timezone: Optional[Union[timezone, str]]
    routes: Optional[List["APIGateHandler"]]
    root_path: Optional[str]
    middleware: Optional[Sequence["Middleware"]]
    exception_handlers: Optional["ExceptionHandlers"]
    on_shutdown: Optional[List["LifeSpanHandler"]]
    on_startup: Optional[List["LifeSpanHandler"]]
    lifespan: Optional[Callable[..., Any]]
    tags: Optional[List[str]]
    include_in_schema: Optional[bool]
    deprecated: Optional[bool]
    enable_openapi: Optional[bool]
    redirect_slashes: Optional[bool]
    async_exit_config: Optional["AsyncExitConfig"]

    class Config(BaseConfig):
        arbitrary_types_allowed = True

from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

from openapi_schemas_pydantic.v3_1_0 import Contact, License, SecurityScheme, Tag
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.types import Lifespan

from esmerald import __version__
from esmerald.conf.enums import EnvironmentType
from esmerald.config import CORSConfig, CSRFConfig, OpenAPIConfig, SessionConfig, StaticFilesConfig
from esmerald.config.asyncexit import AsyncExitConfig
from esmerald.interceptors.types import Interceptor
from esmerald.permissions.types import Permission
from esmerald.pluggables import Pluggable
from esmerald.types import (
    APIGateHandler,
    Dependencies,
    ExceptionHandlerMap,
    LifeSpanHandler,
    Middleware,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
)

if TYPE_CHECKING:
    from esmerald.routing.router import Include
    from esmerald.types import TemplateConfig


class EsmeraldAPISettings(BaseSettings):
    debug: bool = False
    environment: Optional[str] = EnvironmentType.PRODUCTION
    app_name: str = "Esmerald"
    title: str = "Esmerald"
    description: str = "Highly scalable, performant, easy to learn and for every application."
    contact: Optional[Contact] = Contact(name="admin", email="admin@myapp.com")
    summary: str = "Esmerald application"
    terms_of_service: Optional[AnyUrl] = None
    license: Optional[License] = None
    security: Optional[List[SecurityScheme]] = None
    servers: List[Dict[str, Union[str, Any]]] = [{"url": "/"}]
    secret_key: str = "my secret"
    version: str = __version__
    openapi_version: str = "3.1.0"
    allowed_hosts: Optional[List[str]] = ["*"]
    allow_origins: Optional[List[str]] = None
    response_class: Optional[ResponseType] = None
    response_cookies: Optional[ResponseCookies] = None
    response_headers: Optional[ResponseHeaders] = None
    include_in_schema: bool = True
    tags: Optional[List[Tag]] = None
    timezone: str = "UTC"
    use_tz: bool = False
    root_path: Optional[str] = ""
    enable_sync_handlers: bool = True
    enable_scheduler: bool = False
    enable_openapi: bool = True
    redirect_slashes: bool = True
    root_path_in_servers: bool = True
    openapi_url: Optional[str] = "/openapi.json"
    docs_url: Optional[str] = "/docs/swagger"
    redoc_url: Optional[str] = "/docs/redoc"
    swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect"
    redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    redoc_favicon_url: str = "https://esmerald.dev/statics/images/favicon.ico"
    swagger_ui_init_oauth: Optional[Dict[str, Any]] = None
    swagger_ui_parameters: Optional[Dict[str, Any]] = None
    swagger_js_url: str = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.1.3/swagger-ui-bundle.min.js"
    )
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.1.3/swagger-ui.min.css"
    swagger_favicon_url: str = "https://esmerald.dev/statics/images/favicon.ico"

    # Model configuration
    model_config = SettingsConfigDict(extra="allow", ignored_types=(cached_property,))

    # Shell configuration
    ipython_args: List[str] = ["--no-banner"]
    ptpython_config_file: str = "~/.config/ptpython/config.py"

    @property
    def reload(self) -> bool:
        """
        Returns reloading for dev and test environments.
        """
        if self.environment in [EnvironmentType.DEVELOPMENT, EnvironmentType.TESTING]:
            return True
        return False

    @property
    def password_hashers(self) -> List[str]:
        return [
            "esmerald.contrib.auth.hashers.PBKDF2PasswordHasher",
            "esmerald.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        ]

    @property
    def routes(self) -> List[Union[APIGateHandler, "Include"]]:
        """
        Property that can be used as an entrypoint for the base app routes and to start the application.

        Example:
            from esmerald import Include

            class MySettings(EsmeraldAPISettings):
                @property
                def routes(self):
                    return Include(path='/api/v1/', namespace='myapp.routes')
        """
        return []

    @property
    def csrf_config(self) -> Optional[CSRFConfig]:
        """
        Initial Default configuration for the CSRF.
        This can be overwritten in another setting or simply override `secret` or then override
        the `def csrf_config()` property to change the behavior of the whole csrf_config.

        Default:
            None

        Example:

            class MySettings(EsmeraldAPISettings):
                secret: str = "n(0t=%_amauq1m&6sde4z#3mkdmfcad1942ny&#sjp1oygk-5_"

                @property
                def csrf_config(self) -> CSRFConfig:
                    if not self.secret_key:
                        raise ImproperlyConfigured("`secret` setting not configured.")
                    return CSRFConfig(secret=self.secret_key)
        """
        return None

    @property
    def async_exit_config(self) -> AsyncExitConfig:
        """
        Initial Default configuration for the CSRF.
        This can be overwritten in another setting or simply override `secret` or then override
        the `def async_exit_config()` property to change the behavior of the whole async_exit_config.

        This replaces the classic:
        `async_exit_config: Optional[AsyncExitConfig] = None`.

        Default:
            AsyncExitConfig

        Example:

            class MySettings(EsmeraldAPISettings):
                @property
                def async_exit_config(self) -> AsyncExitConfig:
                    ...
        """
        return AsyncExitConfig()

    @property
    def template_config(self) -> Optional["TemplateConfig"]:
        """
        Initial Default configuration for the TemplateConfig.
        This can be overwritten in another setting or simply override `template_config` or then override
        the `def template_config()` property to change the behavior of the whole template_config.

        Esmerald can also support other engines like mako, Diazo, Cheetah. Currently natively
        only supports jinja2 and mako.

        Default:
            JinjaTemplateEngine

        Example:

            class MySettings(EsmeraldAPISettings):
                @property
                def template_config(self) -> "TemplateConfig":
                    TemplateConfig(directory='templates', engine=MakoTemplateEngine)
        """
        return None

    @property
    def static_files_config(self) -> Optional[StaticFilesConfig]:
        """
        Simple configuration indicating where the statics will be placed in
        the application.

        Default:
            None

        Example:

            class MySettings(EsmeraldAPISettings):
                @property
                def static_files_config(self) -> StaticFilesConfig:
                    StaticFilesConfig(path='/', directories=...)
        """
        return None

    @property
    def cors_config(self) -> Optional[CORSConfig]:
        """
        Initial Default configuration for the CORS.
        This can be overwritten in another setting or simply override `allow_origins` or then override
        the `def cors_config()` property to change the behavior of the whole cors_config.

        Default:
            CORSConfig

        Example:

            class MySettings(EsmeraldAPISettings):
                allow_origins: List[str] = ['www.example.com', 'www.foobar.com']

                @property
                def cors_config(self) -> CORSConfig:
                    ...
        """
        if not self.allow_origins:
            return None
        return CORSConfig(allow_origins=self.allow_origins)

    @property
    def session_config(self) -> Optional[SessionConfig]:
        """
        Initial Default configuration for the SessionConfig.
        This can be overwritten in another setting or simply override `session_config` or then override
        the `def session_config()` property to change the behavior of the whole session_config.

        Default:
            None

        Example:

            class MySettings(EsmeraldAPISettings):
                @property
                def session_config(self) -> SessionConfig:
                    SessionConfig(engine=MakoTemplateEngine)
        """
        return None

    @property
    def openapi_config(self) -> OpenAPIConfig:
        """
        Initial Default configuration for the OpenAPI.
        This can be overwritten in another setting or simply override `openapi_config` or then override the `def openapi_config()` property to change the behavior.

        Default:
            OpenAPIConfig

        Example:

            class MySettings(EsmeraldAPISettings):

                @property
                def openapi_config(self) -> OpenAPIConfig:
                    ...
        """
        return OpenAPIConfig(
            title=self.title,
            version=self.version,
            contact=self.contact,
            description=self.description,
            terms_of_service=self.terms_of_service,
            license=self.license,
            servers=self.servers,
            summary=self.summary,
            security=self.security,
            tags=self.tags,
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            swagger_ui_oauth2_redirect_url=self.swagger_ui_oauth2_redirect_url,
            redoc_js_url=self.redoc_js_url,
            redoc_favicon_url=self.redoc_favicon_url,
            swagger_ui_init_oauth=self.swagger_ui_init_oauth,
            swagger_ui_parameters=self.swagger_ui_parameters,
            swagger_js_url=self.swagger_js_url,
            swagger_css_url=self.swagger_css_url,
            swagger_favicon_url=self.swagger_favicon_url,
            root_path_in_servers=self.root_path_in_servers,
            openapi_version=self.openapi_version,
            openapi_url=self.openapi_url,
        )

    @property
    def middleware(self) -> Sequence[Middleware]:
        """
        Initial Default configuration for the middleware.
        This can be overwritten in another setting or simply override `def middleware()`.

        Example:

            class MySettings(EsmeraldAPISettings):

                @property
                def middleware(self) -> List[Middleware]:
                    return [EsmeraldMiddleware]
        """
        return []

    @property
    def scheduler_class(self) -> Any:
        """
        Scheduler class to be used within the application.
        """
        if not self.enable_scheduler:
            return None

        try:
            from asyncz.schedulers import AsyncIOScheduler
        except ImportError as e:
            raise ImportError(
                "The scheduler must be installed. You can do it with `pip install esmerald[schedulers]`"
            ) from e
        return AsyncIOScheduler

    @property
    def scheduler_tasks(self) -> Dict[str, str]:
        """Returns a dict of tasks for run with `scheduler_class`.

        Where the tasks are placed is not linked to the name of
        the file itself. They can be anywhere. What is imoprtant
        is that in the dictionary the name of the task and the
        location of the file where the task is.

        Returns:
            Dict[str, str]: A list of tasks.

        Example:

            class MySettings(EsmeraldAPISettings):

                @property
                def scheduler_tasks(self) -> Dict[str, str]:
                    tasks = {
                        "send_newslettters": "accounts.tasks",
                        "check_balances": "finances.balance_tasks",
                    }

        """

        return {}

    @property
    def scheduler_configurations(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Returns a dict of configurations for run with `scheduler_class`.

        Example:

            class MySettings(EsmeraldAPISettings):

                @property
                def scheduler_configurations(self) -> Dict[str, str]:
                    configurations = {
                        'apscheduler.stores.mongo': {
                            'type': 'mongodb'
                        },
                        'apscheduler.stores.default': {
                            'type': 'sqlalchemy',
                            'url': 'sqlite:///jobs.sqlite'
                        },
                        'apscheduler.executors.default': {
                            'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
                            'max_workers': '20'
                        },
                        'apscheduler.executors.processpool': {
                            'type': 'processpool',
                            'max_workers': '5'
                        },
                        'apscheduler.task_defaults.coalesce': 'false',
                        'apscheduler.task_defaults.max_instances': '3',
                        'apscheduler.timezone': 'UTC',
                    }
        """

        return {}

    @property
    def interceptors(self) -> List[Interceptor]:
        """
        Returns the default interceptors of Esmerald.
        """
        return []

    @property
    def permissions(self) -> List[Permission]:
        """
        Returns the default permissions of Esmerald.
        """
        return []

    @property
    def dependencies(self) -> Dependencies:
        """
        Returns the dependencies of Esmerald main app.
        """
        return {}

    @property
    def exception_handlers(self) -> ExceptionHandlerMap:
        """
        Default exception handlers to be loaded when the application starts
        """
        return {}

    @property
    def on_startup(self) -> Union[List[LifeSpanHandler], None]:
        """
        List of events/actions to be done on_startup.
        """
        return None

    @property
    def on_shutdown(self) -> Union[List[LifeSpanHandler], None]:
        """
        List of events/actions to be done on_shutdown.
        """
        return None

    @property
    def lifespan(self) -> Optional["Lifespan"]:
        """
        Custom lifespan that can be passed instead of the default Starlette.

        The lifespan context function is a newer style that replaces
        on_startup / on_shutdown handlers. Use one or the other, not both.
        """
        return None

    @property
    def pluggables(self) -> Dict[str, "Pluggable"]:
        """
        A pluggable is whatever adds extra level of functionality to
        your an Esmerald application and is used as support for your application.

        Can be from databases, to stores to whatever you desire.
        """
        return {}

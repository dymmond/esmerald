from typing import TYPE_CHECKING, Any, AsyncContextManager, Callable, Dict, List, Optional, Union

from openapi_schemas_pydantic.v3_1_0 import License, SecurityRequirement, Server
from pydantic import BaseConfig, BaseSettings

from esmerald import __version__
from esmerald.conf.enums import EnvironmentType
from esmerald.config import CORSConfig, CSRFConfig, OpenAPIConfig, SessionConfig, StaticFilesConfig
from esmerald.config.asyncexit import AsyncExitConfig
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

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.types import TemplateConfig


class EsmeraldAPISettings(BaseSettings):
    debug: bool = False
    environment: Optional[str] = EnvironmentType.PRODUCTION
    app_name: str = "Esmerald"
    title: str = "My awesome Esmerald application"
    description: str = "Highly scalable, performant, easy to learn and for every application."
    contact: Optional[Dict[str, Union[str, Any]]] = {
        "name": "admin",
        "email": "admin@myapp.com",
    }
    summary: str = "Esmerald application"
    terms_of_service: Optional[str] = None
    license: Optional[License] = None
    security: Optional[List[SecurityRequirement]] = None
    servers: List[Server] = [Server(url="/")]
    secret_key: str = "my secret"
    version: str = __version__
    allowed_hosts: Optional[List[str]] = ["*"]
    allow_origins: Optional[List[str]] = None
    response_class: Optional[ResponseType] = None
    response_cookies: Optional[ResponseCookies] = None
    response_headers: Optional[ResponseHeaders] = None
    include_in_schema: bool = True
    tags: Optional[List[str]] = None
    timezone: str = "UTC"
    use_tz: bool = False
    root_path: Optional[str] = ""
    enable_sync_handlers: bool = True
    enable_scheduler: bool = False
    enable_openapi: bool = True
    redirect_slashes: bool = True

    class Config(BaseConfig):
        extra = "allow"

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
    def routes(self) -> List[APIGateHandler]:
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
    def csrf_config(self) -> CSRFConfig:
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
    def template_config(self) -> "TemplateConfig":
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
    def static_files_config(self) -> StaticFilesConfig:
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
    def cors_config(self) -> CORSConfig:
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
    def session_config(self) -> SessionConfig:
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
        from esmerald.openapi.apiview import OpenAPIView

        return OpenAPIConfig(
            openapi_apiview=OpenAPIView,
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
        )

    @property
    def middleware(self) -> List[Middleware]:
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
    def scheduler_class(self) -> SchedulerType:
        """
        Scheduler class to be used within the application.
        """
        if not self.enable_scheduler:
            return None

        try:
            from asyncz.schedulers import AsyncIOScheduler
        except ImportError:
            raise ImportError(
                "The scheduler must be installed. You can do it with `pip install esmerald[schedulers]`"
            )
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
                        'apscheduler.jobstores.mongo': {
                            'type': 'mongodb'
                        },
                        'apscheduler.jobstores.default': {
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
                        'apscheduler.job_defaults.coalesce': 'false',
                        'apscheduler.job_defaults.max_instances': '3',
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
    def exception_handlers(self) -> ExceptionHandlers:
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
    def lifespan(self) -> Callable[["Esmerald"], AsyncContextManager]:
        """
        Custom lifespan that can be passed instead of the default Starlette.

        The lifespan context function is a newer style that replaces
        on_startup / on_shutdown handlers. Use one or the other, not both.
        """
        return None

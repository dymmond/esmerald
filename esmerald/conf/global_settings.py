from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

from openapi_schemas_pydantic.v3_1_0 import Contact, License, SecurityScheme
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.types import Lifespan
from typing_extensions import Annotated, Doc

from esmerald import __version__
from esmerald.conf.enums import EnvironmentType
from esmerald.config import CORSConfig, CSRFConfig, OpenAPIConfig, SessionConfig, StaticFilesConfig
from esmerald.config.asyncexit import AsyncExitConfig
from esmerald.interceptors.types import Interceptor
from esmerald.permissions.types import Permission
from esmerald.pluggables import Pluggable
from esmerald.routing import gateways
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
    from esmerald.routing.router import Include  # pragma: no cover
    from esmerald.types import TemplateConfig  # pragma: no cover


class EsmeraldAPISettings(BaseSettings):
    """
    `EsmeraldAPISettings` settings object. The main entry-point for any settings
    used by **any** Esmerald application.

    Usually, when creating an application you will need some sort of organisation
    and some sort of settings. Esmerald comes with a native settings system where
    you will only need to inherit, override and add your own extra settings and
    use them anywhere.

    When no values are provided upon an instantiation of an `Esmerald` object, these
    settings are used as the defaults.

    !!! Tip
        The settings system is extremely powerful and must be leveraged accordingly.
        Read more about how to use the [settings](https://esmerald.dev/application/settings/)
        and how you can take advantage of the system.

    **Example**

    ```python
    from esmerald import EsmeraldAPISettings
    from esmerald.conf.enums import EnvironmentType

    class AppSettings(EsmeraldAPISettings):
        '''
        Create your own custom settings.
        '''
        debug: bool = False
        environment: Optional[str] = EnvironmentType.TESTING
    ```
    """

    debug: Annotated[
        bool,
        Doc(
            """
            Boolean indicating if the application should return the debug tracebacks on
            server errors, in other words, if you want to have debug errors being displayed.

            Read more about this in the official [Starlette documentation](https://www.starlette.io/applications/#instantiating-the-application).

            !!! Tip
                Do not use this in production as `True`.
            """
        ),
    ] = False
    environment: Annotated[
        Optional[str],
        Doc(
            """
            Optional string indicating the environment where the settings are running.
            You won't probably need this but it is here in case you might want to use.
            """
        ),
    ] = EnvironmentType.PRODUCTION
    app_name: Annotated[
        str,
        Doc(
            """
            The name of the Esmerald application/API. This name is displayed when the
            [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
            """
        ),
    ] = "Esmerald"
    title: Annotated[
        str,
        Doc(
            """
            The title of the Esmerald application/API. This title is displayed when the
            [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
            """
        ),
    ] = "Esmerald"
    version: Annotated[
        str,
        Doc(
            """
            The version of the Esmerald application/API. This version is displayed when the
            [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

            **Note**: This is the version of your application/API and not th version of the
            OpenAPI specification being used by Esmerald.
            """
        ),
    ] = __version__
    summary: Annotated[
        str,
        Doc(
            """
            The summary of the Esmerald application/API. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
            """
        ),
    ] = "Esmerald application"
    description: Annotated[
        str,
        Doc(
            """
            The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
            """
        ),
    ] = "Highly scalable, performant, easy to learn and for every application."
    contact: Annotated[
        Optional[Contact],
        Doc(
            """
            A dictionary or an object of type `openapi_schemas_pydantic.v3_1_0.Contact` containing the contact information of the application/API.

            Both dictionary and object contain several fields.

            * **name** - String name of the contact.
            * **url** - String URL of the contact. It **must** be in the format of a URL.
            * **email** - String email address of the contact. It **must** be in the format
            of an email address.
            """
        ),
    ] = Contact(name="admin", email="admin@myapp.com")
    terms_of_service: Annotated[
        Optional[AnyUrl],
        Doc(
            """
            A URL pointing to the Terms of Service of the application.
            This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
            """
        ),
    ] = None
    license: Annotated[
        Optional[License],
        Doc(
            """
            A dictionary or an object of type `openapi_schemas_pydantic.v3_1_0.License` containing the license information of the application/API.

            Both dictionary and object contain several fields.

            * **name** - String name of the license.
            * **identifier** - An [SPDX](https://spdx.dev/) license expression.
            * **url** - String URL of the contact. It **must** be in the format of a URL.
            """
        ),
    ] = None
    security: Annotated[
        Optional[List[SecurityScheme]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Esmerald offers some out of the box solutions where this is implemented.

            The [Esmerald security](https://esmerald.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://esmerald.dev/application/levels/).

            For custom security objects, you **must** subclass
            `esmerald.openapi.security.base.HTTPBase` object.
            """
        ),
    ] = None
    servers: Annotated[
        List[Dict[str, Union[str, Any]]],
        Doc(
            """
            A `list` of python dictionaries with the information regarding the connectivity
            to the target.

            This can be useful, for example, if your application is served from different domains and you want a shared OpenAPI documentation to test it all.

            Esmerald automatically handles the OpenAPI documentation generation for you but
            sometimes you might want to add an extra custom domain to it.

            For example, when using `ChildEsmerald` modules, since the object itself subclasses
            Esmerald, that also means you can have independent documentation directly in the
            ChildEsmerald or access the [top level](https://esmerald.dev/application/levels/)
            documentation (the application itself) where you can select the server to test it.

            If the servers `list` is not provided or an is an empty `list`, the default value
            will be a `dict` with the `url` pointing to `/`.

            Each `dict` of the `list` follows the following format for the parameters:

            * **url** - A URL string to the target host/domain. The URL may support server
            variables and it may be also a relative server (for example, the domain/path of a `ChildEsmerald`).
            * **description** - An optional string description of the host/domain.
            * **variables** - A dictionary between the variable and its value. The value
            is used for substitution in the servers URL template. E.g.: `/my-domain/{age: int}`.

            You can read more about how the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
            """
        ),
    ] = [{"url": "/"}]
    secret_key: Annotated[
        str,
        Doc(
            """
            A unique string value used for the cryptography. This value is also
            used internally by Esmerald with the JWT as well the
            [CSRFConfig](https://esmerald.dev/configurations/csrf/).

            !!! Tip
                Make sure you do not reuse the same secret key across environments as
                this can lead to security issues that you can easily avoid.
            """
        ),
    ] = "my secret"
    openapi_version: Annotated[
        str,
        Doc(
            """
            The string version of the OpenAPI.

            Esmerald will generate the OpenAPI 3.1.0 by default and will
            output that as the OpenAPI version.

            If you need to somehow trick some of the tools you are using
            by setting a different version of the OpenAPI, this is the
            field you can use to do it so.
            """
        ),
    ] = "3.1.0"
    allowed_hosts: Annotated[
        Optional[List[str]],
        Doc(
            """
            A `list` of allowed hosts for the application. The allowed hosts when not specified
            defaults to `["*"]` but when specified.

            The allowed hosts are also what controls the
            [TrustedHostMiddleware](https://esmerald.dev/middleware/middleware/#trustedhostmiddleware) and you can read more about how to use it.
            """
        ),
    ] = ["*"]
    allow_origins: Annotated[
        Optional[List[str]],
        Doc(
            """
            A `list` of allowed origins hosts for the application.

            The allowed origins is used by the [CORSConfig](https://esmerald.dev/configurations/cors/) and controls the [CORSMiddleware](https://esmerald.dev/middleware/middleware/#corsmiddleware).

            !!! Tip
                If you create your own [CORSConfig](https://esmerald.dev/configurations/cors/),
                this setting **is ignored** and your custom config takes priority.
            """
        ),
    ] = None
    response_class: Annotated[
        Optional[ResponseType],
        Doc(
            """
            Global default response class to be used within the
            Esmerald application.

            Read more about the [Responses](https://esmerald.dev/responses/) and how
            to use them.
            """
        ),
    ] = None
    response_cookies: Annotated[
        Optional[ResponseCookies],
        Doc(
            """
            A global sequence of `esmerald.datastructures.Cookie` objects.

            Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
            """
        ),
    ] = None
    response_headers: Annotated[
        Optional[ResponseHeaders],
        Doc(
            """
            A global mapping of `esmerald.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).
            """
        ),
    ] = None
    include_in_schema: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if all the routes of the application
            should be included in the OpenAPI documentation.

            **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means when the application
            level is set to `include_in_schema=False`, no schemas will be
            displayed in the OpenAPI documentation.

            !!! Tip
                This can be particularly useful if you have, for example, a `ChildEsmerald` and
                you don't want to include in the schema the routes of the said `ChildEsmerald`.
                This way there is no reason to do it route by route and instead you can
                simply do it directly in the application [level](https://esmerald.dev/application/levels/).
            """
        ),
    ] = True
    tags: Annotated[
        Optional[List[str]],
        Doc(
            """
            A list of strings/enums tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
            these tags on a Esmerald instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ] = None
    timezone: Annotated[
        str,
        Doc(
            """
            Object of time `datetime.timezone` or string indicating the
            timezone for the application.

            **Note** - The timezone is internally used for the supported
            scheduler.
            """
        ),
    ] = "UTC"
    root_path: Annotated[
        Optional[str],
        Doc(
            """
            A path prefix that is handled by a proxy not seen in the
            application but seen by external libraries.

            This affects the tools like the OpenAPI documentation.
            """
        ),
    ] = ""
    enable_sync_handlers: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating the the sync handlers should be allowed in the
            application or not.

            When the `enable_sync_handlers` is set to `False` then only
            `async` handlers are allowed in the application.

            !!! Warning
                Be careful when disabling the `enable_sync_handlers`. When this happens,
                only `async` is allowed in the handlers.
            """
        ),
    ] = True
    enable_scheduler: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the internal scheduler should be enabled
            or not.
            """
        ),
    ] = False
    enable_openapi: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the OpenAPI documentation should
            be generated or not.

            When `False`, no OpenAPI documentation is accessible.

            !!! Tip
                Disable this option if you run in production and no one should access the
                documentation unless behind an authentication.
            ```
            """
        ),
    ] = True
    redirect_slashes: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the redirect slashes are enabled for the
            routes or not.
            ```
            """
        ),
    ] = True
    root_path_in_servers: Annotated[
        bool,
        Doc(
            """
            Boolean flag use to disable the automatic URL generation in the `servers` field
            in the OpenAPI documentation.
            """
        ),
    ] = True
    webhooks: Annotated[
        Optional[Sequence[gateways.WebhookGateway]],
        Doc(
            """
            This is the same principle of the `routes` but for OpenAPI webhooks.

            Read more [about webhooks](https://esmerald.dev/routing/webhooks).

            When a webhook is added, it will automatically add them into the
            OpenAPI documentation.
            """
        ),
    ] = None
    openapi_url: Annotated[
        Optional[str],
        Doc(
            """
            The URL where the OpenAPI schema will be served from.
            The default is `/openapi.json`.

            **Example**

            ```python
            from esmerald import Esmerald

            app = Esmerald(openapi_url="/api/v1/openapi.json")
            ```
            """
        ),
    ] = "/openapi.json"
    docs_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Swagger documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/swagger"
    redoc_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the ReDoc documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/redoc"
    swagger_ui_oauth2_redirect_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Swagger UI OAuth Redirect URL
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/oauth2-redirect"
    redoc_js_url: Annotated[
        str,
        Doc(
            """
            String default relative URL where the ReDoc Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    redoc_favicon_url: Annotated[
        str,
        Doc(
            """
            String default relative URL where the ReDoc favicon is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://esmerald.dev/statics/images/favicon.ico"
    swagger_ui_init_oauth: Annotated[
        Optional[Dict[str, Any]],
        Doc(
            """
            String default relative URL where the Swagger Init Auth documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = None
    swagger_ui_parameters: Annotated[
        Optional[Dict[str, Any]],
        Doc(
            """
            A mapping with parameters to be passed onto Swagger.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = None
    swagger_js_url: Annotated[
        str,
        Doc(
            """
            String default relative URL where the Swagger Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.1.3/swagger-ui-bundle.min.js"
    swagger_css_url: Annotated[
        str,
        Doc(
            """
            String default relative URL where the Swagger CSS is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.1.3/swagger-ui.min.css"
    swagger_favicon_url: Annotated[
        str,
        Doc(
            """
            String default relative URL where the Swagger favicon is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://esmerald.dev/statics/images/favicon.ico"
    with_google_fonts: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating if the google fonts shall be used
            in the ReDoc OpenAPI Documentation.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = True
    stoplight_js_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Stoplight Javascript is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://unpkg.com/@stoplight/elements/web-components.min.js"
    stoplight_css_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Stoplight CSS is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://unpkg.com/@stoplight/elements/styles.min.css"
    stoplight_url: Annotated[
        Optional[str],
        Doc(
            """
            String default relative URL where the Stoplight documentation
            shall be accessed in the application.

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "/docs/elements"
    stoplight_favicon_url: Annotated[
        str,
        Doc(
            """
            String default relative URL where the Stoplight favicon is located
            and used within OpenAPI documentation,

            This is used as the default if no [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/) is provided.
            """
        ),
    ] = "https://esmerald.dev/statics/images/favicon.ico"

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
            with_google_fonts=self.with_google_fonts,
            webhooks=self.webhooks,
            stoplight_css_url=self.stoplight_css_url,
            stoplight_js_url=self.stoplight_js_url,
            stoplight_url=self.stoplight_url,
            stoplight_favicon_url=self.stoplight_favicon_url,
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

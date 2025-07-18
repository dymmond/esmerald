import warnings
from collections.abc import Callable, Iterable, Sequence
from contextlib import asynccontextmanager
from datetime import timezone as dtimezone
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Optional,
    TypeVar,
    Union,
    cast,
)

from lilya.apps import BaseLilya
from lilya.conf import _monkay  # noqa
from lilya.logging import setup_logging
from lilya.middleware import DefineMiddleware  # noqa
from lilya.types import Lifespan, Receive, Scope, Send
from monkay import load
from pydantic import AnyUrl, ValidationError
from typing_extensions import Annotated, Doc

from esmerald.conf import monkay as monkay_for_settings
from esmerald.conf.global_settings import EsmeraldSettings
from esmerald.contrib.schedulers.base import SchedulerConfig
from esmerald.core.config import (
    CORSConfig,
    CSRFConfig,
    LoggingConfig,
    OpenAPIConfig,
    SessionConfig,
    StaticFilesConfig,
)
from esmerald.core.datastructures import State
from esmerald.core.interceptors.types import Interceptor
from esmerald.core.protocols.template import TemplateEngineProtocol
from esmerald.encoders import (
    Encoder,
    MsgSpecEncoder,
    PydanticEncoder,
    register_esmerald_encoder,
)
from esmerald.exception_handlers import (
    improperly_configured_exception_handler,
    pydantic_validation_error_handler,
    validation_error_exception_handler,
)
from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.middleware.asyncexitstack import AsyncExitStackMiddleware
from esmerald.middleware.cors import CORSMiddleware
from esmerald.middleware.csrf import CSRFMiddleware
from esmerald.middleware.exceptions import (
    EsmeraldAPIExceptionMiddleware,
    ExceptionMiddleware,
)
from esmerald.middleware.sessions import SessionMiddleware
from esmerald.middleware.trustedhost import TrustedHostMiddleware
from esmerald.openapi.schemas.v3_1_0 import Contact, License, SecurityScheme
from esmerald.openapi.schemas.v3_1_0.open_api import OpenAPI
from esmerald.permissions.types import Permission
from esmerald.permissions.utils import is_esmerald_permission, wrap_permission
from esmerald.pluggables import Extension, ExtensionDict, Pluggable
from esmerald.routing import gateways
from esmerald.routing.apis import base
from esmerald.routing.router import (
    HTTPHandler,
    Include,
    Router,
    RoutingMethodsMixin,
    WebhookHandler,
    WebSocketHandler,
)
from esmerald.types import (
    APIGateHandler,
    ASGIApp,
    Dependencies,
    ExceptionHandlerMap,
    LifeSpanHandler,
    Middleware,
    ParentType,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
    RouteParent,
)
from esmerald.utils.helpers import is_class_and_subclass

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.core.datastructures import Secret
    from esmerald.types import SettingsType, TemplateConfig

AppType = TypeVar("AppType", bound="Esmerald")


class Application(BaseLilya):
    """
    `Esmerald` application object. The main entry-point for any application/API
    with Esmerald.

    This object is complex and very powerful. Read more in detail about [how to start](https://esmerald.dev/esmerald/) and spin-up an application in minutes.

    !!! Tip
        All the parameters available in the object have defaults being loaded by the
        [settings system](https://esmerald.dev/application/settings/) if nothing is provided.

    **Note**: More details about the defaults in the [settings reference](./application/settings.md).

    ## Example

    ```python
    from esmerald import Esmerald.

    app = Esmerald()
    ```
    """

    register_as_global_instance: ClassVar[bool] = False
    router: "Router"

    __slots__ = (
        "allow_origins",
        "allowed_hosts",
        "app_name",
        "contact",
        "cors_config",
        "csrf_config",
        "debug",
        "dependencies",
        "deprecated",
        "description",
        "enable_openapi",
        "enable_scheduler",
        "exception_handlers",
        "include_in_schema",
        "interceptors",
        "license",
        "middleware",
        "openapi_config",
        "openapi_schema",
        "parent",
        "permissions",
        "extensions",
        "redirect_slashes",
        "response_class",
        "response_cookies",
        "response_headers",
        "root_path",
        "scheduler_config",
        "secret",
        "security",
        "servers",
        "session_config",
        "static_files_config",
        "summary",
        "tags",
        "template_config",
        "terms_of_service",
        "timezone",
        "title",
        "version",
        "encoders",
        "before_request",
        "after_request",
        "logging_config",
    )
    settings_module: Optional[EsmeraldSettings]

    def __init__(
        self,
        *,
        settings_module: Annotated[
            Union[Optional["SettingsType"], Optional[str]],
            Doc(
                """
                Alternative settings parameter. This parameter is an alternative to
                `ESMERALD_SETTINGS_MODULE` way of loading your settings into an Esmerald application.

                When the `settings_module` is provided, it will make sure it takes priority over
                any other settings provided for the instance.

                Read more about the [settings module](https://esmerald.dev/application/settings/)
                and how you can leverage it in your application.

                !!! Tip
                    The settings module can be very useful if you want to have, for example, a
                    [ChildEsmerald](https://esmerald.dev/routing/router/?h=childe#child-esmerald-application) that needs completely different settings
                    from the main app.

                    Example: A `ChildEsmerald` that takes care of the authentication into a cloud
                    provider such as AWS and handles the `boto3` module.
                """
            ),
        ] = None,
        debug: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean indicating if the application should return the debug tracebacks on
                server errors, in other words, if you want to have debug errors being displayed.

                Read more about this in the official [Lilya documentation](https://www.lilya.dev/applications/#applications).

                !!! Tip
                    Do not use this in production.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(debug=True)
                ```
                """
            ),
        ] = None,
        app_name: Annotated[
            Optional[str],
            Doc(
                """
                The name of the Esmerald application/API. This name is displayed when the
                [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(app_name="Esmerald")
                ```
                """
            ),
        ] = None,
        title: Annotated[
            Optional[str],
            Doc(
                """
                The title of the Esmerald application/API. This title is displayed when the
                [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(title="My awesome Esmerald application")
                ```
                """
            ),
        ] = None,
        version: Annotated[
            Optional[str],
            Doc(
                """
                The version of the Esmerald application/API. This version is displayed when the
                [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Note**: This is the version of your application/API and not th version of the
                OpenAPI specification being used by Esmerald.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(version="0.1.0")
                ```
                """
            ),
        ] = None,
        summary: Annotated[
            Optional[str],
            Doc(
                """
                The summary of the Esmerald application/API. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(summary="Black Window joins The Pretenders.")
                ```
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(
                    description='''
                                Black Window joins The Pretenders.

                                ## Powers

                                You can **activate_powers**

                                ## Skills

                                * **read_skill**
                                * **use_skill**
                                '''
                )
                ```
                """
            ),
        ] = None,
        contact: Annotated[
            Optional[Contact],
            Doc(
                """
                A dictionary or an object of type `esmerald.openapi.schemas.v3_1_0.Contact` containing the contact information of the application/API.

                Both dictionary and object contain several fields.

                * **name** - String name of the contact.
                * **url** - String URL of the contact. It **must** be in the format of a URL.
                * **email** - String email address of the contact. It **must** be in the format
                of an email address.

                **Example with object**

                ```python
                from esmerald import Esmerald
                from esmerald.openapi.schemas.v3_1_0 import Contact

                contact = Contact(
                    name="Black Window",
                    url="https://thepretenders.com/open-for-business",
                    email="black.window@thepretenders.com,
                )

                app = Esmerald(contact=contact)
                ```

                **Example with dictionary**

                ```python
                from esmerald import Esmerald

                app = Esmerald(contact={
                    "name": "Black Window",
                    "url": "https://thepretenders.com/open-for-business",
                    "email": "black.window@thepretenders.com,
                })
                ```
                """
            ),
        ] = None,
        terms_of_service: Annotated[
            Optional[AnyUrl],
            Doc(
                """
                A URL pointing to the Terms of Service of the application.
                This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(terms_of_service="https://example.com/terms-of-service")
                ```
                """
            ),
        ] = None,
        license: Annotated[
            Optional[License],
            Doc(
                """
                A dictionary or an object of type `esmerald.openapi.schemas.v3_1_0.License` containing the license information of the application/API.

                Both dictionary and object contain several fields.

                * **name** - String name of the license.
                * **identifier** - An [SPDX](https://spdx.dev/) license expression.
                * **url** - String URL of the contact. It **must** be in the format of a URL.

                **Example with object**

                ```python
                from esmerald import Esmerald
                from esmerald.openapi.schemas.v3_1_0 import License

                license = License(
                    name="MIT",
                    url="https://opensource.org/license/mit/",
                )

                app = Esmerald(license=license)
                ```

                **Example with dictionary**

                ```python
                from esmerald import Esmerald

                app = Esmerald(license={
                    "name": "MIT",
                    "url": "https://opensource.org/license/mit/",
                })
                ```
                """
            ),
        ] = None,
        security: Annotated[
            Optional[list[SecurityScheme]],
            Doc(
                """
                Used by OpenAPI definition, the security must be compliant with the norms.
                Esmerald offers some out of the box solutions where this is implemented.

                The [Esmerald security](https://esmerald.dev/openapi/) is available to automatically used.

                The security can be applied also on a [level basis](https://esmerald.dev/application/levels/).

                For custom security objects, you **must** subclass
                `esmerald.openapi.security.base.HTTPBase` object.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.openapi.security.http import Bearer

                app = Esmerald(security=[Bearer()])
                ```
                """
            ),
        ] = None,
        servers: Annotated[
            Optional[list[dict[str, Union[str, Any]]]],
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

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(
                    servers=[
                        {"url": "https://testing.example.com", "description": "Testing environment"},
                        {"url": "https://uat.example.com", "description": "UAT environment"},
                        {"url": "https://live.example.com", "description": "Production environment"},
                    ]
                )
                ```
                """
            ),
        ] = None,
        secret_key: Annotated[
            Union[Optional[str], Optional["Secret"]],
            Doc(
                """
                A unique string value used for the cryptography. This value is also
                used internally by Esmerald with the JWT as well the
                [CSRFConfig](https://esmerald.dev/configurations/csrf/).

                !!! Tip
                    Make sure you do not reuse the same secret key across environments as
                    this can lead to security issues that you can easily avoid.

                **Example**

                ```python
                from esmerald import Esmerald

                aop = Esmerald(
                    secret_key="p7!3cq1rapxd!@l=gz-&&k*h8sk_n8#1#+n6&q@cb&r!^z^2!g"
                )
                ```
                """
            ),
        ] = None,
        allowed_hosts: Annotated[
            Optional[list[str]],
            Doc(
                """
                A `list` of allowed hosts for the application. The allowed hosts when not specified
                defaults to `["*"]` but when specified.

                The allowed hosts are also what controls the
                [TrustedHostMiddleware](https://esmerald.dev/middleware/middleware/#trustedhostmiddleware) and you can read more about how to use it.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(
                    allowed_hosts=["*.example.com", "www.foobar.com"]
                )
                ```
                """
            ),
        ] = None,
        allow_origins: Annotated[
            Optional[list[str]],
            Doc(
                """
                A `list` of allowed origins hosts for the application.

                The allowed origins is used by the [CORSConfig](https://esmerald.dev/configurations/cors/) and controls the [CORSMiddleware](https://esmerald.dev/middleware/middleware/#corsmiddleware).

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(allow_origins=["*"])
                ```

                !!! Tip
                    If you create your own [CORSConfig](https://esmerald.dev/configurations/cors/),
                    this setting **is ignored** and your custom config takes priority.
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A `list` of global permissions from objects inheriting from
                `esmerald.permissions.BasePermission`.

                Read more about how to implement the [Permissions](https://esmerald.dev/permissions/#basepermission-and-custom-permissions) in Esmerald and to leverage them.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these permissions on a Esmerald instance, means **the whole application**.

                **Example**

                ```python
                from esmerald import Esmerald, BasePermission, Request
                from esmerald.types import APIGateHandler


                class IsAdmin(BasePermission):
                    '''
                    Permissions for admin
                    '''
                    async def has_permission(self, request: "Request", apiview: "APIGateHandler"):
                        is_admin = request.headers.get("admin", False)
                        return bool(is_admin)


                app = Esmerald(permissions=[IsAdmin])
                ```
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A `list` of global interceptors from objects inheriting from
                `esmerald.interceptors.interceptor.EsmeraldInterceptor`.

                Read more about how to implement the [Interceptors](https://esmerald.dev/interceptors/) in Esmerald and to leverage them.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these interceptors on a Esmerald instance, means **the whole application**.

                **Example**

                ```python
                from loguru import logger
                from lilya.types import Receive, Scope, Send

                from esmerald import Esmerald
                from esmerald import EsmeraldInterceptor


                class LoggingInterceptor(EsmeraldInterceptor):
                    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                        # Log a message here
                        logger.info("This is my interceptor being called before reaching the handler.")


                app = Esmerald(interceptors=[LoggingInterceptor])
                ```
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of global dependencies. These dependencies will be
                applied to each **path** of the application.

                Read more about [Dependencies](https://esmerald.dev/dependencies/).

                **Example**

                ```python
                from esmerald import Esmerald, Inject

                def is_valid(number: int) -> bool:
                    return number >= 5

                app = Esmerald(
                    dependencies={
                        "is_valid": Inject(is_valid)
                    }
                )
                ```
                """
            ),
        ] = None,
        csrf_config: Annotated[
            Optional["CSRFConfig"],
            Doc(
                """
                An instance of [CRSFConfig](https://esmerald.dev/configurations/csrf/).

                This configuration is passed to the [CSRFMiddleware](https://esmerald.dev/middleware/middleware/#csrfmiddleware) and enables the middleware.

                !!! Tip
                    You can creatye your own `CRSFMiddleware` version and pass your own
                    configurations. You don't need to use the built-in version although it
                    is recommended to do it so.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.config import CSRFConfig

                csrf_config = CSRFConfig(secret="your-long-unique-secret")

                app = Esmerald(csrf_config=csrf_config)
                ```
                """
            ),
        ] = None,
        openapi_config: Annotated[
            Optional["OpenAPIConfig"],
            Doc(
                """
                An instance of [OpenAPIConfig](https://esmerald.dev/configurations/openapi/config/).

                This object is then used by Esmerald to create the [OpenAPI](https://esmerald.dev/openapi/) documentation.

                **Note**: Here is where the defaults for Esmerald OpenAPI are overriden and if
                this object is passed, then the previous defaults of the settings are ignored.

                !!! Tip
                    This is the way you could override the defaults all in one go
                    instead of doing attribute by attribute.

                **Example**

                ```python
                from esmerald import OpenAPIConfig

                openapi_config = OpenAPIConfig(
                    title="Black Window",
                    openapi_url="/openapi.json",
                    docs_url="/docs/swagger",
                    redoc_url="/docs/redoc",
                )

                app = Esmerald(openapi_config=openapi_config)
                ```
                """
            ),
        ] = None,
        openapi_version: Annotated[
            Optional[str],
            Doc(
                """
                The string version of the OpenAPI.

                Esmerald will generate the OpenAPI 3.1.0 by default and will
                output that as the OpenAPI version.

                If you need to somehow trick some of the tools you are using
                by setting a different version of the OpenAPI, this is the
                field you can use to do it so.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(openapi_version="3.1.0")
                ```
                """
            ),
        ] = None,
        cors_config: Annotated[
            Optional["CORSConfig"],
            Doc(
                """
                An instance of [CORSConfig](https://esmerald.dev/configurations/cors/).

                This configuration is passed to the [CORSMiddleware](https://esmerald.dev/middleware/middleware/#corsmiddleware) and enables the middleware.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.config import CSRFConfig

                cors_config = CORSConfig(allow_origins=["*"])

                app = Esmerald(cors_config=cors_config)
                ```
                """
            ),
        ] = None,
        static_files_config: Annotated[
            Union[
                "StaticFilesConfig",
                list["StaticFilesConfig"],
                tuple["StaticFilesConfig", ...],
                None,
            ],
            Doc(
                """
                An instance of [StaticFilesConfig](https://esmerald.dev/configurations/staticfiles/).

                This configuration is used to enable and serve static files via
                Esmerald application. You can pass also multiple objects via a list or tuple.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.config import StaticFilesConfig

                static_files_config = StaticFilesConfig(
                    path="/static", directory=Path("static")
                )

                app = Esmerald(static_files_config=static_files_config)
                ```
                """
            ),
        ] = None,
        template_config: Annotated[
            Optional["TemplateConfig"],
            Doc(
                """
                An instance of [TemplateConfig](https://esmerald.dev/configurations/template/).

                This configuration is a simple set of configurations that when passed enables the template engine.

                !!! Note
                    You might need to install the template engine before
                    using this. You can always run
                    `pip install esmerald[templates]` to help you out.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.core.config.template import TemplateConfig
                from esmerald.template.jinja import JinjaTemplateEngine

                template_config = TemplateConfig(
                    directory=Path("templates"),
                    engine=JinjaTemplateEngine,
                )

                app = Esmerald(template_config=template_config)
                ```
                """
            ),
        ] = None,
        session_config: Annotated[
            Optional["SessionConfig"],
            Doc(
                """
                An instance of [SessionConfig](https://esmerald.dev/configurations/session/).

                This configuration is passed to the [SessionMiddleware](https://esmerald.dev/middleware/middleware/#sessionmiddleware) and enables the middleware.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.config import SessionConfig

                session_config = SessionConfig(
                    secret_key=settings.secret_key,
                    session_cookie="session",
                )

                app = Esmerald(session_config=session_config)
                ```
                """
            ),
        ] = None,
        logging_config: Annotated[
            Optional["LoggingConfig"],
            Doc(
                """
                An instance of [LoggingConfig](https://esmerald.dev/configurations/logging/).

                """
            ),
        ] = None,
        response_class: Annotated[
            Optional["ResponseType"],
            Doc(
                """
                Global default response class to be used within the
                Esmerald application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import Esmerald, JSONResponse

                app = Esmerald(response_class=JSONResponse)
                ```
                """
            ),
        ] = None,
        response_cookies: Annotated[
            Optional["ResponseCookies"],
            Doc(
                """
                A global sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                app = Esmerald(response_cookies=response_cookies)
                ```
                """
            ),
        ] = None,
        response_headers: Annotated[
            Optional["ResponseHeaders"],
            Doc(
                """
                A global mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                app = Esmerald(response_headers=response_headers)
                ```
                """
            ),
        ] = None,
        scheduler_config: Annotated[
            Optional["SchedulerConfig"],
            Doc(
                """
                Esmerald comes with an internal scheduler connfiguration that can be used to schedule tasks with any scheduler at your choice.


                Esmerald also integrates out of the box with [Asyncz](https://asyncz.tarsild.io/)
                and the scheduler class is nothing more than the `AsyncIOScheduler` provided
                by the library.

                !!! Tip
                    You can create your own scheduler class and use it with Esmerald.
                    For that you must read the [Asyncz](https://asyncz.tarsild.io/schedulers/)
                    documentation and how to make it happen.

                **Note** - To enable the scheduler, you **must** set the `enable_scheduler=True`.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.contrib.scheduler.asyncz.config import AsynczConfig

                scheduler_config = AsynczConfig()

                app = Esmerald(scheduler_config=scheduler_config)
                ```
                """
            ),
        ] = None,
        enable_scheduler: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag indicating if the internal scheduler should be enabled
                or not.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(enable_scheduler=True)
                ```
                """
            ),
        ] = None,
        timezone: Annotated[
            Optional[Union[dtimezone, str]],
            Doc(
                """
                Object of time `datetime.timezone` or string indicating the
                timezone for the application.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(timezone="UTC")
                ```
                """
            ),
        ] = None,
        routes: Annotated[
            Optional[Sequence[Union["APIGateHandler", "Include"]]],
            Doc(
                """
                A global `list` of esmerald routes. Those routes may vary and those can
                be `Gateway`, `WebSocketGateWay` or even `Include`.

                This is also the entry-point for the routes of the application itself
                but it **does not rely on only one [level](https://esmerald.dev/application/levels/)**.

                Read more about how to use and leverage
                the [Esmerald routing system](https://esmerald.dev/routing/routes/).

                **Example**

                ```python
                from esmerald import Esmerald, Gateway, Request, get, Include


                @get()
                async def homepage(request: Request) -> str:
                    return "Hello, home!"


                @get()
                async def another(request: Request) -> str:
                    return "Hello, another!"

                app = Esmerald(
                    routes=[
                        Gateway(handler=homepage)
                        Include("/nested", routes=[
                            Gateway(handler=another)
                        ])
                    ]
                )
                ```

                !!! Note
                    The routing system is very powerful and this example
                    is not enough to understand what more things you can do.
                    Read in [more detail](https://esmerald.dev/routing/routes/) about this.
                """
            ),
        ] = None,
        root_path: Annotated[
            Optional[str],
            Doc(
                """
                A path prefix that is handled by a proxy not seen in the
                application but seen by external libraries.

                This affects the tools like the OpenAPI documentation.

                **Example^^

                ```python
                from esmerald import Esmerald

                app = Esmerald(root_path="/api/v3")
                ```
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[Sequence["Middleware"]],
            Doc(
                """
                A global sequence of Lilya middlewares or `esmerald.middlewares` that are
                used by the application.

                Read more about the [Middleware](https://esmerald.dev/middleware/middleware/).

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.middleware import HTTPSRedirectMiddleware, TrustedHostMiddleware

                app = Esmerald(
                    routes=[...],
                    middleware=[
                        DefineMiddleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]),
                        DefineMiddleware(HTTPSRedirectMiddleware),
                    ],
                )
                ```
                """
            ),
        ] = None,
        encoders: Annotated[
            Optional[Sequence[Union[Encoder, type[Encoder]]]],
            Doc(
                """
            A `list` of encoders to be used by the application once it
            starts.

            Returns:
                list of encoders

            **Example**

            ```python
            from typing import Any

            from attrs import asdict, define, field, has
            from esmerald.encoders import Encoder


            class AttrsEncoder(Encoder):

                def is_type(self, value: Any) -> bool:
                    return has(value)

                def serialize(self, obj: Any) -> Any:
                    return asdict(obj)

                def encode(self, annotation: Any, value: Any) -> Any:
                    return annotation(**value)


            class AppSettings(EsmeraldSettings):

                @property
                def encoders(self) -> Union[list[Encoder], None]:
                    return [AttrsEncoder]
            ```
            """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A global dictionary with handlers for exceptions.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these exception handlers on a Esmerald instance, means **the whole application**.

                Read more about the [Exception handlers](https://esmerald.dev/exception-handlers/).

                **Example**

                ```python
                from pydantic.error_wrappers import ValidationError
                from esmerald import (
                    Esmerald,
                    JSONResponse,
                    Request,
                    ValidationErrorException,
                )

                async def validation_error_exception_handler(
                    request: Request, exc: ValidationError
                ) -> JSONResponse:
                    extra = getattr(exc, "extra", None)
                    if extra:
                        return JSONResponse(
                            {"detail": exc.detail, "errors": exc.extra.get("extra", {})},
                            status_code=status.HTTP_400_BAD_REQUEST,
                        )
                    else:
                        return JSONResponse(
                            {"detail": exc.detail},
                            status_code=status.HTTP_400_BAD_REQUEST,
                        )

                app = Esmerald(
                    exception_handlers={
                            ValidationErrorException: validation_error_exception_handler,
                        },
                )
                ```
                """
            ),
        ] = None,
        on_startup: Annotated[
            Optional[list["LifeSpanHandler"]],
            Doc(
                """
                A `list` of events that are trigger upon the application
                starts.

                Read more about the [events](https://esmerald.dev/lifespan-events/).

                **Example**

                ```python
                from pydantic import BaseModel
                from saffier import Database, Registry

                from esmerald import Esmerald, Gateway, post

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                class User(BaseModel):
                    name: str
                    email: str
                    password: str
                    retype_password: str


                @post("/create", tags=["user"], description="Creates a new user in the database")
                async def create_user(data: User) -> None:
                    # Logic to create the user
                    ...


                app = Esmerald(
                    routes=[Gateway(handler=create_user)],
                    on_startup=[database.connect],
                )
                ```
                """
            ),
        ] = None,
        on_shutdown: Annotated[
            Optional[list["LifeSpanHandler"]],
            Doc(
                """
                A `list` of events that are trigger upon the application
                shuts down.

                Read more about the [events](https://esmerald.dev/lifespan-events/).

                **Example**

                ```python
                from pydantic import BaseModel
                from saffier import Database, Registry

                from esmerald import Esmerald, Gateway, post

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                class User(BaseModel):
                    name: str
                    email: str
                    password: str
                    retype_password: str


                @post("/create", tags=["user"], description="Creates a new user in the database")
                async def create_user(data: User) -> None:
                    # Logic to create the user
                    ...


                app = Esmerald(
                    routes=[Gateway(handler=create_user)],
                    on_shutdown=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        lifespan: Annotated[
            Optional[Lifespan[AppType]],
            Doc(
                """
                A `lifespan` context manager handler. This is an alternative
                to `on_startup` and `on_shutdown` and you **cannot used all combined**.

                Read more about the [lifespan](https://esmerald.dev/lifespan-events/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).

                **Example**

                ```python
                from edgy import Database, Registry

                from esmerald import Esmerald, Request, Gateway, get

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)

                async def create_user(request: Request):
                    # Logic to create the user
                    data = await request.json()
                    ...


                app = Esmerald(
                    routes=[Gateway("/create", handler=create_user)],
                    after_request=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A `list` of events that are trigger after the application
                processes the request.

                Read more about the [events](https://lilya.dev/lifespan/).

                **Example**

                ```python
                from edgy import Database, Registry

                from esmerald import Esmerald, Request, Gateway, get

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                async def create_user(request: Request):
                    # Logic to create the user
                    data = await request.json()
                    ...


                app = Esmerald(
                    routes=[Gateway("/create", handler=create_user)],
                    after_request=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        tags: Annotated[
            Optional[list[str]],
            Doc(
                """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(tags=["application"])
                ```

                **Example with nested routes**

                When tags are added on a level bases, those are concatenated into the
                final handler.

                ```python
                from esmerald import Esmerald, Gateway, get

                @get("/home", tags=["home"])
                async def home() -> dict[str, str]:
                    return {"hello": "world"}


                app = Esmerald(
                    routes=[Gateway(handler=home)],
                    tags=["application"]
                )
                ```
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            Optional[bool],
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

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(include_in_schema=False)
                ```

                 **Example applied to ChildEsmerald**

                ```python
                from esmerald import Esmerald, ChildEsmerald, Include

                app = Esmerald(routes=[
                    Include("/child", app=ChildEsmerald(
                        include_in_schema=False
                    ))
                ])
                ```
                """
            ),
        ] = None,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag indicating if all the routes of the application
                should be deprecated in the OpenAPI documentation.

                !!! Tip
                    This can be particularly useful if you have, for example, a `ChildEsmerald` and
                    you  want to deprecate in favour of a new one being implemented.

                **Example**

                ```python
                from esmerald import Esmerald

                app = Esmerald(deprecated=True)
                ```

                **Example with a ChildEsmerald**

                ```python
                from esmerald import Esmerald, ChildEsmerald, Include

                app = Esmerald(routes=[
                    Include("/child", app=ChildEsmerald(
                        deprecated=True
                    ))
                ])
                ```
                """
            ),
        ] = None,
        enable_openapi: Annotated[
            Optional[bool],
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
        ] = None,
        redirect_slashes: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag indicating if the redirect slashes are enabled for the
                routes or not.
                """
            ),
        ] = None,
        extensions: Annotated[
            Optional[dict[str, Union[Extension, Pluggable, type[Extension], str]]],
            Doc(
                """
                A `list` of global extensions from objects inheriting from
                `esmerald.interceptors.interceptor.EsmeraldInterceptor`.

                Read more about how to implement the [Plugables](https://esmerald.dev/pluggables/) in Esmerald and to leverage them.

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
                        self, app: Optional["Esmerald"] = None, config: PluggableConfig = None, **kwargs: "DictAny"
                    ):
                        super().__init__(app, **kwargs)
                        self.app = app

                    def extend(self, config: PluggableConfig) -> None:
                        logger.success(f"Successfully passed a config {config.name}")


                my_config = PluggableConfig(name="my extension")
                pluggable = Pluggable(MyExtension, config=my_config)


                app = Esmerald(
                    routes=[], extensions={"my-extension": pluggable}
                )
                ```
                """
            ),
        ] = None,
        pluggables: Annotated[
            Optional[dict[str, Union[Extension, Pluggable, type[Extension], str]]],
            Doc(
                """
                THIS PARAMETER IS DEPRECATED USE extensions INSTEAD

                A `list` of global extensions from objects inheriting from
                `esmerald.interceptors.interceptor.EsmeraldInterceptor`.

                Read more about how to implement the [Plugables](https://esmerald.dev/pluggables/) in Esmerald and to leverage them.

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
                        self, app: Optional["Esmerald"] = None, config: PluggableConfig = None, **kwargs: "DictAny"
                    ):
                        super().__init__(app, **kwargs)
                        self.app = app

                    def extend(self, config: PluggableConfig) -> None:
                        logger.success(f"Successfully passed a config {config.name}")


                my_config = PluggableConfig(name="my extension")
                pluggable = Pluggable(MyExtension, config=my_config)


                app = Esmerald(
                    routes=[], extensions={"my-extension": pluggable}
                )
                ```
                """
            ),
        ] = None,
        parent: Annotated[
            Optional[Union["ParentType", "Esmerald", "ChildEsmerald"]],
            Doc(
                """
                Used internally by Esmerald to recognise and build the [application levels](https://esmerald.dev/application/levels/).

                !!! Tip
                    Unless you know what are you doing, it is advisable not to touch this.
                """
            ),
        ] = None,
        root_path_in_servers: Annotated[
            bool,
            Doc(
                """
                Boolean flag use to disable the automatic URL generation in the `servers` field
                in the OpenAPI documentation.

                **Examples**

                ```python
                from esmerald import Esmerald

                app = Esmerald(root_path_in_servers=False)
                ```
                """
            ),
        ] = None,
        webhooks: Annotated[
            Optional[Sequence["gateways.WebhookGateway"]],
            Doc(
                """
                This is the same principle of the `routes` but for OpenAPI webhooks.

                Read more [about webhooks](https://esmerald.dev/routing/webhooks).

                When a webhook is added, it will automatically add them into the
                OpenAPI documentation.
                """
            ),
        ] = None,
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
        ] = None,
    ) -> None:
        self.settings_module = None

        if settings_module is not None and isinstance(settings_module, str):
            settings_module = load(settings_module)

        if settings_module is not None:
            if not isinstance(settings_module, EsmeraldSettings) and not is_class_and_subclass(
                settings_module, EsmeraldSettings
            ):
                raise ImproperlyConfigured(
                    "settings_module must be a subclass of EsmeraldSettings"
                )
            elif isinstance(settings_module, EsmeraldSettings):
                self.settings_module = settings_module  # type: ignore
            elif is_class_and_subclass(settings_module, EsmeraldSettings):
                self.settings_module = settings_module()

        assert lifespan is None or (on_startup is None and on_shutdown is None), (
            "Use either 'lifespan' or 'on_startup'/'on_shutdown', not both."
        )

        if allow_origins and cors_config:
            raise ImproperlyConfigured("It can be only allow_origins or cors_config but not both.")

        self.parent = parent

        self._debug = self.load_settings_value("debug", debug, is_boolean=True)
        self.debug = self._debug

        self.title = self.load_settings_value("title", title)
        self.app_name = self.load_settings_value("app_name", app_name)
        self.description = self.load_settings_value("description", description)
        self.version = self.load_settings_value("version", version)
        self.openapi_version = self.load_settings_value("openapi_version", openapi_version)
        self.summary = self.load_settings_value("summary", summary)
        self.contact = self.load_settings_value("contact", contact)
        self.terms_of_service = self.load_settings_value("terms_of_service", terms_of_service)
        self.license = self.load_settings_value("license", license)
        self.servers = self.load_settings_value("servers", servers)
        self.secret_key = self.load_settings_value("secret_key", secret_key)
        self.allowed_hosts = self.load_settings_value("allowed_hosts", allowed_hosts)
        self.allow_origins = self.load_settings_value("allow_origins", allow_origins)

        self.interceptors = self.load_settings_value("interceptors", interceptors) or []
        self.dependencies = self.load_settings_value("dependencies", dependencies) or {}
        self.csrf_config = self.load_settings_value("csrf_config", csrf_config)
        self.cors_config = self.load_settings_value("cors_config", cors_config)
        self.openapi_config = self.load_settings_value("openapi_config", openapi_config)
        self.template_config = self.load_settings_value("template_config", template_config)
        self.static_files_config = self.load_settings_value(
            "static_files_config", static_files_config
        )
        self.session_config = self.load_settings_value("session_config", session_config)
        self.logging_config = self.load_settings_value("logging_config", logging_config)
        self.response_class = self.load_settings_value("response_class", response_class)
        self.response_cookies = self.load_settings_value("response_cookies", response_cookies)
        self.response_headers = self.load_settings_value("response_headers", response_headers)
        self.enable_scheduler = self.load_settings_value(
            "enable_scheduler", enable_scheduler, is_boolean=True
        )
        self.scheduler_config: "SchedulerConfig" = self.load_settings_value(
            "scheduler_config", scheduler_config
        )
        self.timezone = self.load_settings_value("timezone", timezone)
        self.root_path = self.load_settings_value("root_path", root_path)
        self._middleware = self.load_settings_value("middleware", middleware) or []
        _exception_handlers = self.load_settings_value("exception_handlers", exception_handlers)
        self.exception_handlers = {} if _exception_handlers is None else dict(_exception_handlers)
        self.on_startup = self.load_settings_value("on_startup", on_startup)
        self.on_shutdown = self.load_settings_value("on_shutdown", on_shutdown)
        self.lifespan = self.load_settings_value("lifespan", lifespan)
        self.tags = self.load_settings_value("tags", security)
        self.include_in_schema = self.load_settings_value(
            "include_in_schema", include_in_schema, is_boolean=True
        )
        self.security = self.load_settings_value("security", security)
        self.enable_openapi = self.load_settings_value(
            "enable_openapi", enable_openapi, is_boolean=True
        )
        self.redirect_slashes = self.load_settings_value(
            "redirect_slashes", redirect_slashes, is_boolean=True
        )

        # OpenAPI Related
        self.root_path_in_servers = self.load_settings_value(
            "root_path_in_servers", root_path_in_servers, is_boolean=True
        )

        if not self.include_in_schema or not self.enable_openapi:
            self.root_path_in_servers = False

        self.webhooks = self.load_settings_value("webhooks", webhooks) or []
        self.openapi_url = self.load_settings_value("openapi_url", openapi_url)
        self.tags = self.load_settings_value("tags", tags)

        self.openapi_schema: Optional["OpenAPI"] = None
        self.state: Annotated[
            State,
            Doc(
                """
                The state object for the application. This is always the
                same object across the whole application.

                This can be defined as the application state and not request state
                which means that it does not change each request.

                Learn more in the [Lilya documentation](https://www.lilya.dev/applications/#storing-state-on-the-app-instance).
                """
            ),
        ] = State()
        self.async_exit_config = monkay_for_settings.settings.async_exit_config

        self.encoders = list(
            cast(
                Iterable[Union[Encoder]],
                (
                    encoder if isclass(encoder) else encoder
                    for encoder in self.load_settings_value("encoders", encoders) or []
                ),
            )
        )
        self._register_application_encoders()

        if self.enable_scheduler:
            self.activate_scheduler()

        # Handle permissions
        self.__base_permissions__ = permissions or []
        self.__lilya_permissions__ = [
            wrap_permission(permission)
            for permission in self.load_settings_value("permissions", self.__base_permissions__)
            or []
            if not is_esmerald_permission(permission)
        ]

        self.permissions: Sequence[Permission] = [
            permission
            for permission in self.load_settings_value("permissions", self.__base_permissions__)
            or []
            if is_esmerald_permission(permission)
        ]

        self.before_request_callbacks = (
            self.load_settings_value("before_request", before_request) or []
        )

        self.after_request_callbacks = (
            self.load_settings_value("after_request", after_request) or []
        )

        self.router = Router(
            on_shutdown=self.on_shutdown,
            on_startup=self.on_startup,
            routes=routes,
            app=self,
            lifespan=self.lifespan,
            deprecated=deprecated,
            security=security,
            redirect_slashes=self.redirect_slashes,
            before_request=self.before_request_callbacks,
            after_request=self.after_request_callbacks,
        )
        self.get_default_exception_handlers()
        if self.register_as_global_instance:
            _monkay.set_instance(self)
        self.user_middleware = self.build_user_middleware_stack()
        self.middleware_stack = self.build_middleware_stack()
        self.template_engine = self.get_template_engine(self.template_config)

        # load extensions nearly last so everythings is initialized
        _extensions: Any = self.load_settings_value("extensions", extensions)
        if not _extensions:
            _extensions = self.load_settings_value("pluggables", pluggables)
            if _extensions:
                warnings.warn(
                    "The `pluggables` parameter/setting is deprecated use `extensions` instead",
                    DeprecationWarning,
                    stacklevel=2,
                )

        self.extensions = ExtensionDict(_extensions, app=cast(Esmerald, self))
        self.extensions.extend()
        self._configure()

    @property
    def pluggables(self) -> ExtensionDict:
        warnings.warn(
            "The `pluggables` attribute is deprecated use `extensions` instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.extensions

    def _register_application_encoders(self) -> None:
        """
        Registers the default Esmerald encoders.

        This allows backwards compatibility with the previous
        versions of Esmerald supporting Pydantic and MsgSpec by default.

        This way, the support still remains but using the Lilya Encoders.
        """
        self.register_encoder(cast(Encoder, PydanticEncoder))
        self.register_encoder(cast(Encoder, MsgSpecEncoder))

        for encoder in self.encoders:
            self.register_encoder(encoder)

    def _configure(self) -> None:
        """
        Starts the Esmerald configurations and extras.
        """
        if self.static_files_config:
            for config in (
                self.static_files_config
                if isinstance(self.static_files_config, (list, tuple))
                else [self.static_files_config]
            ):
                static_route = Include(path=config.path, app=config.to_app(), name=config.name)
                self.router.validate_root_route_parent(static_route)
                self.router.routes.append(static_route)

        self.create_webhooks_signature_model(self.webhooks)
        self.activate_openapi()

        if self.logging_config is not None:
            setup_logging(self.logging_config)

    def load_settings_value(
        self, name: str, value: Optional[Any] = None, is_boolean: bool = False
    ) -> Any:
        """
        Loader used to get the settings defaults and custom settings
        of the application.
        """
        if not is_boolean:
            if not value:
                return self.get_settings_value(
                    self.settings_module,
                    monkay_for_settings.settings,
                    name,
                )
            return value

        if value is not None:
            return value
        return self.get_settings_value(
            self.settings_module,
            monkay_for_settings.settings,
            name,
        )

    def create_webhooks_signature_model(self, webhooks: Sequence[gateways.WebhookGateway]) -> None:
        """
        Creates the signature model for the webhooks.
        """
        webhooks = []
        for route in self.webhooks:
            if not isinstance(route, gateways.WebhookGateway):
                raise ImproperlyConfigured(
                    f"The webhooks should be an instances of 'WebhookGateway', got '{route.__class__.__name__}' instead."
                )

            if not is_class_and_subclass(route.handler, base.View) and not isinstance(
                route.handler, base.View
            ):
                if not route.handler.parent:
                    route.handler.parent = route
                    webhooks.append(route)
            else:
                if not route.handler.parent:  # pragma: no cover
                    route(parent=self)  # type: ignore

                handler: base.View = cast("base.View", route.handler)
                route_handlers = handler.get_route_handlers()
                for route_handler in route_handlers:
                    gate = gateways.WebhookGateway(
                        handler=cast(WebhookHandler, route_handler),
                        name=route_handler.fn.__name__,
                    )

                    include_in_schema = (
                        route.include_in_schema
                        if route.include_in_schema is not None
                        else route_handler.include_in_schema
                    )
                    gate.include_in_schema = include_in_schema

                    webhooks.append(gate)
                self.webhooks.pop(self.webhooks.index(route))

        for route in webhooks:
            self.router.create_signature_models(route)
        self.webhooks = webhooks

    def activate_scheduler(self) -> None:
        """
        Makes sure the scheduler is accessible.

        This method checks if the necessary scheduler modules are installed. If not, it raises an ImportError
        with instructions on how to install the scheduler. It then initializes the scheduler with the specified
        parameters or defaults to using the AsyncIOScheduler class.

        :raises ImportError: If the scheduler modules are not installed.
        """
        if self.scheduler_config is None:
            raise ImproperlyConfigured(
                "It cannot start the scheduler if there is no scheduler_config declared."
            )

        if self.lifespan is not None:
            original_lifespan = self.lifespan

            @asynccontextmanager
            async def wrapped_lifespan(app: Esmerald) -> Any:
                # Wraps the original lifespan to include the scheduler start and shutdown.
                await self.scheduler_config.start()
                async with original_lifespan(app):
                    yield
                await self.scheduler_config.shutdown()

            self.lifespan = wrapped_lifespan

        else:
            if self.on_startup is not None:
                self.on_startup.append(self.scheduler_config.start)
            else:
                self.on_startup = [self.scheduler_config.start]

            if self.on_shutdown is not None:
                self.on_shutdown.append(self.scheduler_config.shutdown)
            else:
                self.on_shutdown = [self.scheduler_config.shutdown]

    def get_settings_value(
        self,
        local_settings: Optional["EsmeraldSettings"],
        global_settings: "EsmeraldSettings",
        value: str,
    ) -> Any:
        """Obtains the value from a settings module or defaults to the global settings"""
        setting_value = None

        if local_settings:
            setting_value = getattr(local_settings, value, None)
        if setting_value is None:
            return getattr(global_settings, value, None)
        return setting_value

    def activate_openapi(self) -> None:
        def set_value(value: Any, name: str) -> Any:
            """Sets the value to be passed into the openapi configuration"""
            if value or not getattr(self.openapi_config, name, None):
                setattr(self.openapi_config, name, value)

        if self.enable_openapi:
            set_value(self.title, "title")
            set_value(self.version, "version")
            set_value(self.openapi_version, "openapi_version")
            set_value(self.summary, "summary")
            set_value(self.description, "description")
            set_value(self.contact, "contact")
            set_value(self.tags, "tags")
            set_value(self.servers, "servers")
            set_value(self.terms_of_service, "terms_of_service")
            set_value(self.root_path_in_servers, "root_path_in_servers")
            set_value(self.openapi_url, "openapi_url")

            if self.webhooks or not self.openapi_config.webhooks:
                self.openapi_config.webhooks = self.webhooks

            self.openapi_config.enable(self)

    def get_template_engine(
        self,
        template_config: Annotated[
            "TemplateConfig",
            Doc(
                """
                An instance of [TemplateConfig](https://esmerald.dev/configurations/template/).

                This configuration is a simple set of configurations that when passed enables the template engine.

                !!! Note
                    You might need to install the template engine before
                    using this. You can always run
                    `pip install esmerald[templates]` to help you out.

                **Example**

                ```python
                from esmerald import Esmerald
                from esmerald.core.config.template import TemplateConfig
                from esmerald.template.jinja import JinjaTemplateEngine

                template_config = TemplateConfig(
                    directory=Path("templates"),
                    engine=JinjaTemplateEngine,
                )

                app = Esmerald(template_config=template_config)
                ```
                """
            ),
        ],
    ) -> Optional["TemplateEngineProtocol"]:
        """
        Returns the template engine for the application based on
        the `TemplateConfig` provided.

        **Example**

        ```python
        from esmerald import Esmerald
        from esmerald.core.config.template import TemplateConfig
        from esmerald.template.jinja import JinjaTemplateEngine

        template_config = TemplateConfig(
            directory=Path("templates"),
            engine=JinjaTemplateEngine,
        )

        app = Esmerald()
        engine = app.get_template_engine(template_config=)
        ```
        """
        if not template_config:
            return None

        engine: "TemplateEngineProtocol" = template_config.engine(
            template_config.directory,
            env=template_config.env,
            **template_config.env_options,
        )
        return engine

    def add_apiview(
        self,
        value: Annotated[
            Union["gateways.Gateway", "gateways.WebSocketGateway"],
            Doc(
                """
                The `APIView` or similar to be added.
                """
            ),
        ],
    ) -> None:
        """
        Adds an [APIView](https://esmerald.dev/routing/apiview/) or related
        to the application routing.

        **Example**

        ```python
        from esmerald import Esmerald, APIView, Gateway, get


        class View(APIView):
            path = "/"

            @get(status_code=status_code)
            async def hello(self) -> str:
                return "Hello, World!"


        gateway = Gateway(handler=View)

        app = Esmerald()
        app.add_apiview(value=gateway)
        ```
        """
        self.router.add_apiview(value=value)

    def add_route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        handler: Annotated[
            "HTTPHandler",
            Doc(
                """
                An instance of [handler](https://esmerald.dev/routing/handlers/#http-handlers).
                """
            ),
        ],
        router: Annotated[
            Optional["Router"],
            Doc(
                """
            A `esmerald.Router` instance to where the route will be added to.
            """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list["Middleware"]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `path_for()`.
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
            ),
        ] = True,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        activate_openapi: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if after adding the route
                to the application routing system, if it should
                also be added to the OpenAPI documentation.
                """
            ),
        ] = True,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> None:
        """
        Adds a [Route](https://esmerald.dev/routing/routes/)
        to the application routing.

        This is a dynamic way of adding routes on the fly.

        **Example**

        ```python
        from esmerald import Esmerald, get


        @get(status_code=status_code)
        async def hello() -> str:
            return "Hello, World!"


        app = Esmerald()
        app.add_route(path="/hello", handler=hello)
        ```
        """
        router = router or self.router
        router.add_route(
            path=path,
            handler=handler,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            interceptors=interceptors,
            permissions=permissions,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

        if activate_openapi:
            self.activate_openapi()

    def add_websocket_route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        handler: Annotated[
            "WebSocketHandler",
            Doc(
                """
                An instance of [websocket handler](https://esmerald.dev/routing/handlers/#websocket-handler).
                """
            ),
        ],
        router: Annotated[
            Optional["Router"],
            Doc(
                """
            A `esmerald.Router` instance to where the route will be added to.
            """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the WebSocketGateway. The name can be reversed by `path_for()`.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list["Middleware"]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> None:
        """
        Adds a websocket [Route](https://esmerald.dev/routing/routes/)
        to the application routing.

        This is a dynamic way of adding routes on the fly.

        **Example**

        ```python
        from esmerald import Esmerald, websocket


        @websocket()
        async def websocket_route(socket: WebSocket) -> None:
            await socket.accept()
            data = await socket.receive_json()

            assert data
            await socket.send_json({"data": "esmerald"})
            await socket.close()


        app = Esmerald()
        app.add_websocket_route(path="/ws", handler=websocket_route)
        ```
        """
        router = router or self.router
        return router.add_websocket_route(
            path=path,
            handler=handler,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            interceptors=interceptors,
            permissions=permissions,
            middleware=middleware,
            name=name,
            before_request=before_request,
            after_request=after_request,
        )

    def add_include(
        self,
        include: Annotated[
            Include,
            Doc(
                """
                The [Include](https://esmerald.dev/routing/routes/#include) instance
                to be added.
                """
            ),
        ],
    ) -> None:
        """
        Adds an [Include](https://esmerald.dev/routing/routes/#include) directly to the active application router
        and creates the proper signature models.

        **Example**

        ```python
        from esmerald import get, Include


        @get(status_code=status_code)
        async def hello(self) -> str:
            return "Hello, World!"


        include = Include("/child", routes=[Gateway(handler=hello)])

        app = Esmerald()
        app.add_include(include=include)
        ```
        """
        self.router.routes.append(include)

        for route in include.routes:
            self.router.create_signature_models(route)

        self.activate_openapi()

    def add_child_esmerald(
        self,
        path: str,
        child: Annotated[
            "ChildEsmerald",
            Doc(
                """
                The [ChildEsmerald](https://esmerald.dev/routing/router/#child-esmerald-application) instance
                to be added.
                """
            ),
        ],
        name: Optional[str] = None,
        middleware: Optional[Sequence["Middleware"]] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlerMap"] = None,
        interceptors: Optional[list["Interceptor"]] = None,
        permissions: Optional[list["Permission"]] = None,
        include_in_schema: Optional[bool] = True,
        deprecated: Optional[bool] = None,
        security: Optional[list["SecurityScheme"]] = None,
        before_request: Union[Sequence[Callable[..., Any]], None] = None,
        after_request: Union[Sequence[Callable[..., Any]], None] = None,
    ) -> None:
        """
        Adds a [ChildEsmerald](https://esmerald.dev/routing/router/#child-esmerald-application) directly to the active application router.

        **Example**

        ```python
        from esmerald import get, Include, ChildEsmerald, Esmerald

        @get(status_code=status_code)
        async def hello(self) -> str:
            return "Hello, World!"

        child = ChildEsmerald(routes=[Gateway(handler=hello)])

        app = Esmerald()
        app.add_child_esmerald(path"/child", child=child)
        ```
        """
        if not isinstance(child, ChildEsmerald):
            raise ImproperlyConfigured("The child must be an instance of a ChildEsmerald.")

        self.router.routes.append(
            Include(
                path=path,
                name=name,
                app=child,
                parent=self.router,
                dependencies=dependencies,
                middleware=cast("list[Middleware]", middleware),
                exception_handlers=exception_handlers,
                interceptors=interceptors,
                permissions=permissions,
                include_in_schema=include_in_schema,
                deprecated=deprecated,
                security=security,
                before_request=before_request,
                after_request=after_request,
            )
        )
        self.activate_openapi()

    def add_router(
        self,
        router: Annotated[
            "Router",
            Doc(
                """
                The [Router](https://esmerald.dev/routing/router/) instance to be
                added.
                """
            ),
        ],
    ) -> None:
        """
        Adds a [Router](https://esmerald.dev/routing/router/) directly to the active application router.

        **Example**

        ```python
        from esmerald import get
        from esmerald.routing.router import Router


        @get(status_code=status_code)
        async def hello(self) -> str:
            return "Hello, World!"


        router = Router(path="/aditional", routes=[Gateway(handler=hello)])

        app = Esmerald()
        app.add_router(router=router)
        ```
        """
        for route in router.routes:
            if isinstance(route, Include):
                self.router.routes.append(
                    Include(
                        path=route.path,
                        app=route.app,
                        dependencies=route.dependencies,
                        exception_handlers=route.exception_handlers,
                        name=route.name,
                        middleware=cast("list[Middleware]", route.middleware),
                        interceptors=route.interceptors,
                        permissions=route.permissions,
                        routes=cast("Sequence[Union[APIGateHandler, Include]]", route.routes),
                        parent=self.router,
                        security=route.security,
                        before_request=route.before_request,
                        after_request=route.after_request,
                    )
                )
                continue

            gateway = (
                gateways.Gateway
                if not isinstance(route.handler, WebSocketHandler)
                else gateways.WebSocketGateway
            )

            if self.on_startup:
                self.on_startup.extend(router.on_startup)
            if self.on_shutdown:
                self.on_shutdown.extend(router.on_shutdown)

            self.router.routes.append(
                gateway(
                    path=route.path,
                    dependencies=route.dependencies,
                    exception_handlers=route.exception_handlers,
                    name=route.name,
                    middleware=route.middleware,
                    interceptors=route.interceptors,
                    permissions=route.permissions,
                    handler=route.handler,
                    parent=self.router,
                    is_from_router=True,
                    before_request=route.before_request,
                    after_request=route.after_request,
                )
            )

        self.activate_openapi()

    def get_default_exception_handlers(self) -> None:
        """
        Default exception handlers added to the application.
        Defaulting the HTTPException and ValidationError handlers to JSONResponse.

        The values can be overritten by calling the self.add_event_handler().

        Example:
            app = Esmerald()

            app.add_event_handler(HTTPException, my_new_handler)
            app.add_event_handler(ValidationError, my_new_422_handler)

        """
        self.exception_handlers.setdefault(
            ImproperlyConfigured, improperly_configured_exception_handler
        )
        self.exception_handlers.setdefault(
            ValidationErrorException, validation_error_exception_handler
        )

        self.exception_handlers.setdefault(ValidationError, pydantic_validation_error_handler)

    def build_routes_exception_handlers(
        self,
        route: "RouteParent",
        exception_handlers: Optional[dict[str, Callable[..., Any]]] = None,
    ) -> dict[str, Callable[..., Any]]:
        """
        Builds the exception handlers stack from the top to the bottom of the routes.
        """
        if not exception_handlers:
            exception_handlers = {}

        if isinstance(route, Include):
            exception_handlers.update(route.exception_handlers)
            app = getattr(route, "app", None)
            if app and isinstance(app, (Esmerald, ChildEsmerald)):
                return exception_handlers

            for _route in route.routes:
                exception_handlers = self.build_routes_exception_handlers(
                    _route, exception_handlers
                )

        if isinstance(route, (gateways.Gateway, gateways.WebSocketGateway)):
            exception_handlers.update(route.exception_handlers)
            if route.handler.exception_handlers:
                exception_handlers.update(route.handler.exception_handlers)

        return exception_handlers

    def build_user_middleware_stack(self) -> list["DefineMiddleware"]:
        """
        Configures all the passed settings
        and wraps inside an exception handler.

        CORS, CSRF, TrustedHost and JWT are provided to the __init__ they will wapr the
        handler as well.

        It evaluates the middleware passed into the routes from bottom up
        """
        user_middleware = []

        if self.allowed_hosts:
            user_middleware.append(
                DefineMiddleware(TrustedHostMiddleware, allowed_hosts=self.allowed_hosts)
            )
        if self.cors_config:
            user_middleware.append(
                DefineMiddleware(CORSMiddleware, **self.cors_config.model_dump())
            )
        if self.csrf_config:
            user_middleware.append(
                DefineMiddleware(CSRFMiddleware, **self.csrf_config.model_dump())
            )

        if self.session_config:
            user_middleware.append(
                DefineMiddleware(SessionMiddleware, **self.session_config.model_dump())
            )

        for middleware in self._middleware or []:
            if isinstance(middleware, DefineMiddleware):
                user_middleware.append(middleware)
            else:
                user_middleware.append(DefineMiddleware(middleware))  # type: ignore
        return user_middleware

    def build_middleware_stack(self) -> "ASGIApp":
        """
        Esmerald uses the [esmerald.core.protocols.MiddlewareProtocol] (interfaces) and therefore we
        wrap the DefineMiddleware in a slighly different manner.

        Overriding the default build_middleware_stack will allow to control the initial
        middlewares that are loaded by Esmerald. All of these values can be updated.

        For each route, it will verify from top to bottom which exception handlers are being passed
        and called them accordingly.

        For APIViews, since it's a "wrapper", the handler will update the current list to contain
        both.
        """
        debug = self.debug
        error_handler = None
        exception_handlers = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        for route in self.routes or []:
            exception_handlers.update(self.build_routes_exception_handlers(route))

        middleware = (
            [
                DefineMiddleware(
                    EsmeraldAPIExceptionMiddleware,
                    exception_handlers=exception_handlers,
                    error_handler=error_handler,
                    debug=debug,
                ),
            ]
            + self.user_middleware
            + [
                DefineMiddleware(
                    ExceptionMiddleware,
                    handlers=exception_handlers,
                    debug=debug,
                ),
                DefineMiddleware(
                    AsyncExitStackMiddleware,
                    config=self.async_exit_config,
                    debug=debug,
                ),
            ]
        )

        app: "ASGIApp" = self.router
        for cls, args, kwargs in reversed(middleware):
            app = cls(app=app, *args, **kwargs)  # noqa
        return app

    def add_extension(
        self, name: str, extension: Union[Extension, Pluggable, type[Extension]]
    ) -> None:
        """
        Adds a [Pluggable](https://esmerald.dev/pluggables/) directly to the active application router.

        **Example**

        ```python
        from loguru import logger
        from esmerald import Esmerald, Extension, Pluggable

        from pydantic import BaseModel


        class Config(BaseModel):
            name: Optional[str]


        class CustomExtension(Extension):
            def __init__(self, app: Optional["Esmerald"] = None, **kwargs: DictAny):
                super().__init__(app, **kwargs)
                self.app = app

            def extend(self, config) -> None:
                logger.success(
                    f"Started standalone plugging with the name: {config.name}"
                )

                # you can also autoadd the extension like this
                # self.app.add_extension(config.name, self)


        app = Esmerald(routes=[])
        config = Config(name="manual")
        pluggable = Pluggable(CustomExtension, config=config)
        app.add_extension("manual", pluggable)
        # or
        # app.add_extension("manual", pluggable)
        ```
        """
        self.extensions[name] = extension

    def add_pluggable(
        self, name: str, extension: Union[Extension, Pluggable, type[Extension]]
    ) -> None:
        warnings.warn(
            "The `add_pluggable` method is deprecated use `add_extension` instead",
            DeprecationWarning,
            stacklevel=2,
        )
        self.add_extension(name, extension)

    @property
    def settings(self) -> "EsmeraldSettings":
        """
        Returns the Esmerald settings object for easy access.

        This `settings` are the ones being used by the application upon
        initialisation.

        **Example**

        ```python
        from esmerald import Esmerald

        app = Esmerald()
        app.settings
        ```
        """
        general_settings = (
            self.settings_module if self.settings_module else monkay_for_settings.settings
        )
        return general_settings

    @property
    def default_settings(
        self,
    ) -> "EsmeraldSettings":
        """
        Returns the default global settings.
        """
        return monkay_for_settings.settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        with monkay_for_settings.with_settings(self.settings):
            if scope["type"] == "lifespan":
                await self.router.lifespan(scope, receive, send)
                return

            if self.root_path:
                scope["root_path"] = self.root_path

            scope["state"] = {}
            await super().__call__(scope, receive, send)

    def websocket_route(self, path: str, name: Optional[str] = None) -> Callable:
        raise ImproperlyConfigured("`websocket_route` is not valid. Use WebSocketGateway instead.")

    def on_event(self, event_type: str) -> Callable:  # pragma: nocover
        """
        Add an event on_startup and on_shutdown with Esmerald underlying
        implementation of the lifespan.

        Check: https://www.esmerald.dev/lifespan-events/
        """
        return self.router.on_event(event_type)

    def add_event_handler(self, event_type: str, func: Callable) -> None:  # pragma: no cover
        self.router.add_event_handler(event_type, func)

    def register_encoder(self, encoder: Encoder) -> None:
        """
        Registers a Encoder into the list of predefined encoders of the system.
        """
        register_esmerald_encoder(encoder)


class Esmerald(RoutingMethodsMixin, Application):
    """
    `Esmerald` application object. The main entry-point for any application/API
    with Esmerald.

    This object is complex and very powerful. Read more in detail about [how to start](https://esmerald.dev/esmerald/) and spin-up an application in minutes.

    !!! Tip
        All the parameters available in the object have defaults being loaded by the
        [settings system](https://esmerald.dev/application/settings/) if nothing is provided.

    **Note**: More details about the defaults in the [settings reference](./application/settings.md).

    ## Example

    ```python
    from esmerald import Esmerald.

    app = Esmerald()
    ```
    """

    register_as_global_instance: ClassVar[bool] = True

    def forward_single_method_route(self, path: str, method: str, **kwargs: Any) -> Callable:
        """For customization, defaults to route."""
        return cast("Callable", getattr(self.router, method.lower())(path=path, **kwargs))

    def route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        methods: Annotated[
            Optional[list[str]],
            Doc(
                """
                A list of HTTP methods to serve the Gateway.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `path_for()`.
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
            ),
        ] = True,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.router.route(
            path=path,
            methods=methods,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
            deprecated=deprecated,
            before_request=before_request,
            after_request=after_request,
        )

    def websocket(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `path_for()`.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[list[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        before_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered before the application processes the request.
                """
            ),
        ] = None,
        after_request: Annotated[
            Union[Sequence[Callable[..., Any]], None],
            Doc(
                """
                A list of events that are triggered after the application processes the request.
                """
            ),
        ] = None,
    ) -> Callable:
        return self.router.websocket(
            path=path,
            name=name,
            dependencies=dependencies,
            interceptors=interceptors,
            permissions=permissions,
            exception_handlers=exception_handlers,
            middleware=middleware,
            before_request=before_request,
            after_request=after_request,
        )


class ChildEsmerald(Esmerald):
    """
    `ChildEsmerald` application object. The main entry-point for a modular application/API
    with Esmerald.

    The `ChildEsmerald` inherits directly from the `Esmerald` object which means all the same
    parameters, attributes and functions of Esmerald ara also available in the `ChildEsmerald`.

    This object is complex and very powerful. Read more in detail about [how to use](https://esmerald.dev/routing/router/?h=childe#child-esmerald-application) and spin-up an application in minutes with `ChildEsmerald`.

    !!! Tip
        All the parameters available in the object have defaults being loaded by the
        [settings system](https://esmerald.dev/application/settings/) if nothing is provided.

    ## Example

    ```python
    from esmerald import Esmerald, ChildEsmerald, Include

    app = Esmerald(routes=[Include("/child", app=ChildEsmerald(...))])
    ```
    """

    register_as_global_instance: bool = False

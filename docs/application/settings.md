# Settings

Every application in a way or another needs settings for the uniqueness of the project itself.

When the complexity of a project increases and there are settings spread across the codebase it is when the things
start to get messy.

One great framework, Django, has the settings in place but because of the legacy codebase and the complexity of almost
20 years of development of the framework, those became a bit bloated and hard to maintain.

Inspired by Django and by the experience of 99% of the developed applications using some sort of settings
(by environment, by user...), Esmerald comes equiped to handle exactly with that natively and using
[Pydantic](https://pydantic-docs.helpmanual.io/visual_studio_code/#basesettings-and-ignoring-pylancepyright-errors)
to leverage those.

!!! Note
    From the version 0.8.X, Esmerald allows settings on [levels](./levels.md) making it 100% modular.

## The way of the settings

There are two ways of using the settings object within an Esmerald application.

* Using the **ESMERALD_SETTINGS_MODULE**
* Using the **[settings_config](#the-settings_config)**

Each one of them has particular use cases but they also work together is perfect harmony.

## EsmeraldAPISettings and the application

When starting a Esmerald instance if no parameters are provided, it will automatically load the defaults from the
system settings object, the `EsmeraldAPISettings`.

=== "No parameters"
ExampleObjectExampleObject
    ```python hl_lines="4"
    {!> ../docs_src/settings/app/no_parameters.py!}
    ```

=== "With Parameters"

    ```python hl_lines="6"
    {!> ../docs_src/settings/app/with_parameters.py!}
    ```

## Custom settings

Using the defaults from `EsmeraldAPISettings` generally will not do too much for majority of the applications.

For that reason custom settings are needed.

**All the custom settings should be inherited from the `EsmeraldAPISettings`**.

Let's assume we have three environment for one application: `production`, `testing`, `development` and a base settings
file that contains common settings across the three environments.

=== "Base"

    ```python
    {!> ../docs_src/settings/custom/base.py!}
    ```

=== "Development"

    ```python
    {!> ../docs_src/settings/custom/development.py!}
    ```

=== "Testing"

    ```python
    {!> ../docs_src/settings/custom/testing.py!}
    ```

=== "Production"

    ```python
    {!> ../docs_src/settings/custom/production.py!}
    ```

What just happened?

1. Created an `AppSettings` inherited from the `EsmeraldAPISettings` with common cross environment properties.
2. Created one settings file per environment and inherited from the base `AppSettings`.
3. Imported specific database settings per environment and added the events `on_startup` and `on_shutdown` specific
to each.

!!! note
    Esmerald supports [Tortoise-ORM](https://tortoise.github.io/) for async SQL databases and therefore has the
    `init_database` and `stop_database` functionality ready to be used.

## Esmerald Settings Module

Esmerald by default is looking for a `ESMERALD_SETTINGS_MODULE` environment variable to execute any custom settings,
if nothing is provided then it will execute the application defaults.

=== "Without ESMERALD_SETTINGS_MODULE"

    ```shell
    uvicorn src:app --reload

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "With ESMERALD_SETTINGS_MODULE"

    ```shell
    ESMERALD_SETTINGS_MODULE=src.configs.production.ProductionSettings uvicorn src:app

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

It is very simple, `ESMERALD_SETTINGS_MODULE` looks for the custom settings class created for the application
and loads it in lazy mode.

## The settings_config

This is a great tool to make your Esmerald applications 100% independent and modular. There are cases
where you simply want to plug an existing esmerald application into another and that same esmerald application
already has unique settings and defaults.

The `settings_config` is a parameter available in every single `Esmerald` instance as well as `ChildEsmerald`.

### Creating a settings_config

The configurations have **literally the same concept**
as the [EsmeraldAPISettings](#esmeraldapisettings-and-the-application), which means that every single
`settings_config` **must be derived from the EsmeraldAPISettings** or an `ImproperlyConfigured` exception
is thrown.

The reason why the above is to keep the integrity of the application and settings.

```python hl_lines="21"
{!> ../docs_src/application/settings/settings_config/example2.py !}
```

Is this simple, literally, Esmerald simplifies the way you can manipulate settings on each level
and keeping the intregrity at the same time.

Check out the [order of priority](#order-of-priority) to understand a bit more.

## Order of priority

There is an order or priority in which Esmerald reads your settings.

If a `settings_config` is passed into an Esmerald instance, that same object takes priority above
anything else. Let us imagine the following:

* An Esmerald application with normal settings.
* A ChildEsmerald with a specific set of configurations unique to it.

```python hl_lines="11"
{!> ../docs_src/application/settings/settings_config/example1.py !}
```

**What is happenening here?**

In the example above we:

1. Created a settings object derived from the main `EsmeraldAPISettings` and
passed some defaults.
1. Passed the `ChildEsmeraldSettings` into the `ChildEsmerald` instance.
2. Passed the `ChildEsmerald` into the `Esmerald` application.

So, how does the priority take place here using the `settings_config`?

1. If no parameter value (upon instantiation), for example `app_name`, is provided, it will check for that same value
inside the `settings_config`.
2. If `settings_config` does not provide an `app_name` value, it will look for the value in the
`ESMERALD_SETTINGS_MODULE`.
3. If no `ESMERALD_SETTINGS_MODULE` environment variable is provided by you, then it will default
to the Esmerald defaults. [Read more about this here](#esmerald-settings-module).

So the order of priority:

1. Parameter instance value takes priority above `settings_config`.
2. `settings_config` takes priority above `ESMERALD_SETTINGS_MODULE`.
3. `ESMERALD_SETTINGS_MODULE` is the last being checked.

## Settings config and Esmerald settings module

The beauty of this modular approach is the fact that makes it possible to use **both** approaches at
the same time ([order of priority](#order-of-priority)).

Let us use an example where:

1. We create a main Esmerald settings object to be used by the `ESMERALD_SETTINGS_MODULE`.
2. We create a `settings_config` to be used by the Esmerald instance.
3. We start the application using both.

Let us also assume you have all the settings inside a `src/configs` directory.

**Create a configuration to be used by the ESMERALD_SETTINGS_MODULE**

```python title="src/configs/main_settings.py"
{!> ../docs_src/application/settings/settings_config/main_settings.py !}
```

**Create a configuration to be used by the setting_config**

```python title="src/configs/app_settings.py"
{!> ../docs_src/application/settings/settings_config/app_settings.py !}
```

**Create an Esmerald instance**

```python title="src/configs/app_settings.py" hl_lines="14"
{!> ../docs_src/application/settings/settings_config/app.py !}
```

Now we can start the server using the `AppSettings` as global and `InstanceSettings` being passed
via instantiation. The AppSettings from the main_settings.py is used to call from the command-line.

```shell
ESMERALD_SETTINGS_MODULE=src.configs.main_settings.AppSettings uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Great! Now not only we have used the `settings_config` and `ESMERALD_SETTINGS_MODULE` but we used
them at the same time!

Check out the [order of priority](#order-of-priority) to understand which value takes precedence
and how Esmerald reads them out.

## Parameters

The parameters available inside `EsmeraldAPISettings` can be overridden by any custom settings.

### The current parameters available inside the `EsmeraldAPISettings`

* **settings_config** - A settings instance, derived from `EsmeraldAPISettings`.

* **debug** - Boolean indicating if a debug tracebacks should be returns on errors. Basically, debug mode,
very useful for development.

    <sup>Default: `False`</sup>

* **environment** - The application environment to be run.

    <sup>Default: `production`</sup>

* **app_name** - The application name. Used for OpenAPI.

    <sup>Default: `Esmerald`</sup>

* **title** - The title for the application. Used for OpenAPI.

    <sup>Default: `My awesome Esmerald app.`</sup>

* **description** - The description for the application. Used for OpenAPI.

    <sup>Default: `Highly scalable, performant, easy to learn and for every application.`</sup>

* **version** - The version for the application. Used for OpenAPI.

    <sup>Default: Same as the Esmerald.</sup>

* **contact** - The contact of an admin. Used for OpenAPI.
    
    <sup>Default: `{"name": "admin", "email": "admin@myapp.com"}`.</sup>

* **terms_of_service** - The terms of service of the application. Used for OpenAPI.

    <sup>Default: `None`.</sup>

* **license** - The license information. Used for OpenAPI.

    <sup>Default: `None`.</sup>

* **servers** - The servers in dictionary format. Used for OpenAPI.

    <sup>Default: `None`.</sup>

* **secret_key** - The secret key used for internal encryption (for example, user passwords). We strongly advise to
update this particular setting, mostly if the application uses the native [Tortoise](../databases/tortoise/tortoise.md)
support.

    <sup>Default: `my secret`</sup>

* **allowed_hosts** - A list of allowed hosts. Enables the built-in allowed hosts middleware.

    <sup>Default: `['*']`</sup>

* **allow_origins** - A list of allowed origins. Enables the built-in CORS middleware. `allow_origins`
or a [CORSConfig](../configurations/cors.md) object but not both.

    <sup>Default: `None`</sup>

* **response_class** - Custom subclass of [Response](../responses.md) to be used as application application response
class.

    <sup>Default: `None`</sup>

* **response_cookies** - List of [cookie](../datastructures.md) objects.

    <sup>Default: `None`</sup>

* **response_headers** - Mapping dictionary of header objects.

    <sup>Default: `None`</sup>

* **scheduler_class** - A [scheduler]('../scheduler/scheduler.md') class used for the application tasks.

    <sup>Default: `AsyncIOScheduler`</sup>

* **scheduler_tasks** - A python dictionary with key and pair values as strings mapping the [scheduler tasks](../scheduler/scheduler.md).

    <sup>Default: `{}`</sup>

* **scheduler_configurations** - A python dictionary with key and pair values as strings mapping the
extra configuations of [scheduler tasks](../scheduler/handler.md).

    <sup>Default: `{}`</sup>

* **enable_scheduler** - Flag indicating if the appliaction `scheduler` should be enabled or not. Defaults to `False`.

    <sup>Default: `False`</sup>

* **timezone** - The application default timezone. Defaults to `UTC`.

    <sup>Default: `UTC`</sup>

* **include_in_schema** - Boolean flag to indicate if should be schema included or not. This is for the whole
application and not only for specific endpoints.

    <sup>Default: `True`</sup>

* **tags** - List of tags to include in the OpenAPI schema.

    <sup>Default: `None`</sup>

* **timezone** - The global timezone used for the application.

    <sup>Default: `UTC`</sup>

* **use_tz** - Boolean flag indicating if TZ should be used.

    <sup>Default: `True`</sup>

* **root_path** - The root path for the application.

    <sup>Default: `""`</sup>

* **enable_sync_handlers** - Boolean flag if set it will allow `sync` functions, except for websockets.

    <sup>Default: `True`</sup>

* **enable_openapi** - Boolean flag indicating if the OpenAPI docs should be generated.

    <sup>Default: `True`</sup>

* **reload** - Boolean flag indicating if reload should happen (by default) on development and testing enviroment.
The default environment is `production`.
  
    <sup>Default: `False`</sup>

* **password_hashers** - A list of [password hashers](../password-hashers.md) used for encryption of the passwords.

    <sup>Default: `["esmerald.contrib.auth.hashers.PBKDF2PasswordHasher",
                    "esmerald.contrib.auth.hashers.PBKDF2SHA1PasswordHasher"]`
    </sup>

    !!! warning
        The password hashers are linked to [Tortoise](../databases/tortoise/tortoise.md) support and are used
        with the models provided by default with Esmerald.

* **routes** - A list of routes to serve incoming HTTP and WebSocket requests.
  
    <sup>Default: `[]`</sup>

    !!! tip
        This property is related to the entrypoint routes of the whole application, meaning, for application level.
        See [Include](../routing/routes.md#include-and-application) and how to use it to leverage the initial
        entrypoint.

    !!! Note
        If we can compare with other frameworks, this is very similar to `URL_CONF` settings from Django.

* **csrf_config** - If [CSRFConfig](../configurations/csrf.md) is set it will enable the CSRF built-in middleware.

    <sup>Default: `None`</sup>

* **template_config** - If [TemplateConfig](../configurations/template.md) is set it will enable the template
engine from the configuration object.

    <sup>Default: `None`</sup>

* **static_files_config** - If [StaticFilesConfig](../configurations/staticfiles.md) is set, it will enable the
application static files configuration.

    <sup>Default: `None`</sup>

* **cors_config** - If [CORSConfig](../configurations/cors.md) is set it will enable the CORS built-in middleware.

    <sup>Default: `CORSConfig` if `allow_origins` is not set.</sup><br>
    <sup>Default: `None` if `allow_origins` is not set.</sup>

* **session_config** - If [SessionConfig](../configurations/session.md) is set it will enable the session
built-in middleware.

    <sup>Default: `None`</sup>

* **openapi_config** - If [OpenAPIConfig](../configurations/openapi/config.md) is set it will override the default OpenAPI
docs settings.

    <sup>Default: `OpenAPIConfig`</sup>

* **middleware** - A list of middleware to run for every request. A Esmerald application will always include the
middlewares from the configurations passed (CSRF, CORS, JWT...) and the custom user middleware. The middlewares
can be subclasses of the [MiddlewareProtocol](../protocols.md).
or <a href='https://www.starlette.io/middleware/' target='_blank'>Starlette Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).

    <sup>Default `[]`</sup>

* **interceptors** - A list of [interceptors](../interceptors.md) to serve the application incoming
requests (HTTP and Websockets).

    <sup>Default `[]`</sup>

* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).

    <sup>Default `[]`</sup>

* **dependencies** - A dictionary of string and [Inject](../dependencies.md) instances enable application level dependency
injection.

    <sup>Default `{}`</sup>

* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.

    <sup>Default `{}`</sup>

* **on_startup** - A list of callables to run on application startup. Startup handler callables do not take any
arguments, and may be be either standard functions, or async functions.

    <sup>Default `None`</sup>

* **on_shutdown** - A list of callables to run on application shutdown. Shutdown handler callables do not take any
arguments, and may be be either standard functions, or async functions.

    <sup>Default `None`</sup>

* **lifepan** - The lifespan context function is a newer style that replaces on_startup / on_shutdown handlers.
Use one or the other, not both.

    <sup>Default `None`</sup>

* **enable_openapi** - If the OpenAPI should be enabled or not.

    <sup>Default `True`</sup>

* **redirect_slashes** - Enable/disable redirect slashes for the handlers.

    <sup>Default `True`</sup>

!!! Check
    All the configurations are pydantic objects. Check [CORS](../configurations/cors.md),
    [CSRF](../configurations/csrf.md), [Session](../configurations/session.md), [JWT](../configurations/session.md),
    [StaticFiles](../configurations/staticfiles.md), [Template](../configurations/template.md) and
    [OpenAPI](../configurations/openapi/config.md) and see how to use them.

## Accessing settings

To access the application settings there are different ways:

=== "Within the application request"

    ```python hl_lines="6"
    {!> ../docs_src/settings/access/within_app.py!}
    ```

=== "From the global settings"

    ```python hl_lines="1 6"
    {!> ../docs_src/settings/access/global.py!}
    ```

=== "From the conf settings"

    ```python hl_lines="2 7"
    {!> ../docs_src/settings/access/conf.py!}
    ```

!!! info
    Some of this information might have been mentioned in some other parts of the documentation but we assume
    the people reading it might have missed.

## Order of importance

Using the settings to start an application instead of providing the parameters directly in the moment of
instantiation does not mean that one will work with the other.

When you instantiate an application **or you pass parameters directly or you use settings or a mix of both**.

Passing parameters in the object will always override the values from the default settings.

```python
from esmerald import EsmeraldAPISettings
from esmerald.conf.enums import EnvironmentType
from esmerald.middleware.basic import BasicHTTPMiddleware
from esmerald.types import Middleware


class AppSettings(EsmeraldAPISettings):
    debug: bool = False

    @property
    def middleware(self) -> List[Middleware]:
        return [BasicHTTPMiddleware]

```

The application will:

1. Start with `debug` as `False`.
2. Will start with a middleware `BasicHTTPMiddleware`.

Starting the application with the above settings will make sure that has an initial `BasicHTTPMiddleware` and `debug`
set with values **but** what happens if you use the settings + parameters on instantiation?

```python
from esmerald import Esmerald

app = Esmerald(debug=True, middleware=[])
```

The application will:

1. Start with `debug` as `True`.
2. Will start without custom middlewares it the `BasicHTTPMiddleware` it was overridden by `[]`.

Although it was set in the settings to start with `BasicHTTPMiddleware` and debug as `False`, once you pass different
values in the moment of instantiating an `Esmerald` object, those will become the values to be used.

**Declaring parameters in the instance will always precede the values from your settings**.

The reason why you should be using settings it is because will make your codebase more organised and easier
to maintain.

!!! Check
    When you pass the parameters via instantiation of an Esmerald object and not via parameters, when accessing the
    values via `request.app.settings`, the values **won't be in the settings** as those were passed via application
    instantiation and not via settings object. The way to access those values is, for example, `request.app.app_name`
    directly.

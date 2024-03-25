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
* Using the **[settings_config](#the-settings_config)** *(deprecated)*
* Using the **[settings_module](#the-settings_module)**

Each one of them has particular use cases but they also work together is perfect harmony.

## EsmeraldAPISettings and the application

When starting a Esmerald instance if no parameters are provided, it will automatically load the defaults from the
system settings object, the `EsmeraldAPISettings`.

=== "No parameters"

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

For consistency, this parameter will be deprecated and `settings_module` will be the official one
to be used. Nothing changes for you except the parameter name. Please refer to [settings_module](#the-settings_module).

!!! Warning
    This property although still available to be used for backwards compatibility, it will be removed
    from verion 2.9.0. Make sure you use [settings_module](#the-settings_module) instead.

## The settings_module

This is a great tool to make your Esmerald applications 100% independent and modular. There are cases
where you simply want to plug an existing esmerald application into another and that same esmerald application
already has unique settings and defaults.

The `settings_module` is a parameter available in every single `Esmerald` instance as well as `ChildEsmerald`.

### Creating a settings_module

The configurations have **literally the same concept**
as the [EsmeraldAPISettings](#esmeraldapisettings-and-the-application), which means that every single
`settings_module` **must be derived from the EsmeraldAPISettings** or an `ImproperlyConfigured` exception
is thrown.

The reason why the above is to keep the integrity of the application and settings.

```python hl_lines="22"
{!> ../docs_src/application/settings/settings_config/example2.py !}
```

Is this simple, literally, Esmerald simplifies the way you can manipulate settings on each level
and keeping the intregrity at the same time.

Check out the [order of priority](#order-of-priority) to understand a bit more.

## Order of priority

There is an order or priority in which Esmerald reads your settings.

If a `settings_module` is passed into an Esmerald instance, that same object takes priority above
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

So, how does the priority take place here using the `settings_module`?

1. If no parameter value (upon instantiation), for example `app_name`, is provided, it will check for that same value
inside the `settings_module`.
2. If `settings_module` does not provide an `app_name` value, it will look for the value in the
`ESMERALD_SETTINGS_MODULE`.
3. If no `ESMERALD_SETTINGS_MODULE` environment variable is provided by you, then it will default
to the Esmerald defaults. [Read more about this here](#esmerald-settings-module).

So the order of priority:

1. Parameter instance value takes priority above `settings_module`.
2. `settings_module` takes priority above `ESMERALD_SETTINGS_MODULE`.
3. `ESMERALD_SETTINGS_MODULE` is the last being checked.

## Settings config and Esmerald settings module

The beauty of this modular approach is the fact that makes it possible to use **both** approaches at
the same time ([order of priority](#order-of-priority)).

Let us use an example where:

1. We create a main Esmerald settings object to be used by the `ESMERALD_SETTINGS_MODULE`.
2. We create a `settings_module` to be used by the Esmerald instance.
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

```python title="src/app.py" hl_lines="14"
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

Great! Now not only we have used the `settings_module` and `ESMERALD_SETTINGS_MODULE` but we used
them at the same time!

Check out the [order of priority](#order-of-priority) to understand which value takes precedence
and how Esmerald reads them out.

## Parameters

The parameters available inside `EsmeraldAPISettings` can be overridden by any custom settings
and those are available in the [settings reference](../references/application/settings.md).

!!! Check
    All the configurations are pydantic objects. Check [CORS](../configurations/cors.md),
    [CSRF](../configurations/csrf.md), [Session](../configurations/session.md), [JWT](../configurations/session.md),
    [StaticFiles](../configurations/staticfiles.md), [Template](../configurations/template.md) and
    [OpenAPI](../configurations/openapi/config.md) and see how to use them.

**Note**: To understand which parameters exist as well the corresponding values, [settings reference](../references/application/settings.md)
is the place to go.

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
from esmerald.middleware.https import HTTPSRedirectMiddleware
from esmerald.types import Middleware
from lilya.middleware import DefineMiddleware


class AppSettings(EsmeraldAPISettings):
    debug: bool = False

    @property
    def middleware(self) -> List[Middleware]:
        return [DefineMiddleware(HTTPSRedirectMiddleware)]

```

The application will:

1. Start with `debug` as `False`.
2. Will start with a middleware `HTTPSRedirectMiddleware`.

Starting the application with the above settings will make sure that has an initial `HTTPSRedirectMiddleware` and `debug`
set with values **but** what happens if you use the settings + parameters on instantiation?

```python
from esmerald import Esmerald

app = Esmerald(debug=True, middleware=[])
```

The application will:

1. Start with `debug` as `True`.
2. Will start without custom middlewares it the `HTTPSRedirectMiddleware` it was overridden by `[]`.

Although it was set in the settings to start with `HTTPSRedirectMiddleware` and debug as `False`, once you pass different
values in the moment of instantiating an `Esmerald` object, those will become the values to be used.

**Declaring parameters in the instance will always precede the values from your settings**.

The reason why you should be using settings it is because will make your codebase more organised and easier
to maintain.

!!! Check
    When you pass the parameters via instantiation of an Esmerald object and not via parameters, when accessing the
    values via `request.app.settings`, the values **won't be in the settings** as those were passed via application
    instantiation and not via settings object. The way to access those values is, for example, `request.app.app_name`
    directly.

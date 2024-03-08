# Applications

Esmerald runs Lilya under the hood and therefore includes an application class **Esmerald** that ties
of its functionality.

## The Esmerald class

=== "In a nutshell"

    ```python
    {!> ../docs_src/application/app/nutshell.py !}
    ```

=== "Another way"

    ```python
    {!> ../docs_src/application/app/another_way.py!}
    ```

=== "With Include"

    ```python
    {!> ../docs_src/application/app/with_include.py!}
    ```

### Quick note

Because the swagger and redoc can only do so much, for example with the
`username = request.path_params["username"]` **you won't be able to test it via docs**.
**The best way of doing it is by calling the API directly via any prefered client or browser.**

In other words, the path param can be captured using the Request.path_params, but cannot be tested from the Swagger UI.

#### Testing using curl or insomnia

Via cURL:

```shell
$ curl -X GET http://localhost:8000/user/esmerald
```

Via Insomnia:

<p align="center">
  <a href="https://res.cloudinary.com/dymmond/image/upload/v1669211317/esmerald/others/insomnia_phitug.png" target="_blank"><img src="https://res.cloudinary.com/dymmond/image/upload/v1669211317/esmerald/others/insomnia_phitug.png" alt='Insomnia'></a>
</p>

!!! Note
    You can use something else besides insomnia. This was for example purposes.

### Instantiating the application

Creating an appliation instance can be done in different ways and with a great plus of using the
[settings](./settings.md) for a cleaner approach.

**Parameters**:

* **debug** - Boolean indicating if a debug tracebacks should be returns on errors. Basically, debug mode,
very useful for development.
* **title** - The title for the application. Used for OpenAPI.
* **app_name** - The application name. Used also for OpenAPI.
* **description** - The description for the application. Used for OpenAPI.
* **version** - The version for the application. Used for OpenAPI.
* **contact** - The contact of an admin. Used for OpenAPI.
* **terms_of_service** - The terms of service of the application. Used for OpenAPI.
* **license** - The license information. Used for OpenAPI.
* **servers** - The servers in dictionary format. Used for OpenAPI.
* **secret_key** - The secret key used for internal encryption (for example, user passwords).
* **allowed_hosts** - A list of allowed hosts. Enables the built-in allowed hosts middleware.
* **allow_origins** - A list of allowed origins. Enables the built-in CORS middleware. It can be only `allow_origins`
or a [CORSConfig](../configurations/cors.md) object but not both.
* **routes** - A list of routes to serve incoming HTTP and WebSocket requests.
A list of [Gateway](../routing/routes.md#gateway), [WebSocketGateway](../routing/routes.md#websocketgateway)
or [Include](../routing/routes.md#include)
* **interceptors** - A list of [interceptors](../interceptors.md) to serve the application incoming
requests (HTTP and Websockets).
* **permissions** - A list of [permissions](../permissions.md) to serve the application incoming
requests (HTTP and Websockets).
* **middleware** - A list of middleware to run for every request. A Esmerald application will always include the
middlewares from the configurations passed (CSRF, CORS, JWT...) and the custom user middleware. The middlewares
can be subclasses of the [MiddlewareProtocol](../protocols.md).
or <a href='https://www.lilya.dev/middleware/' target='_blank'>Lilya Middleware</a> as they are both converted
internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
* **dependencies** - A dictionary of string and [Inject](.././dependencies.md) instances enable application level dependency
injection.
* **exception handlers** - A dictionary of [exception types](../exceptions.md) (or custom exceptions) and the handler
functions on an application top level. Exception handler callables should be of the form of
`handler(request, exc) -> response` and may be be either standard functions, or async functions.
* **csrf_config** - If [CSRFConfig](../configurations/csrf.md) is set it will enable the CSRF built-in middleware.
* **openapi_config** - If [OpenAPIConfig](../configurations/openapi/config.md) is set it will override the default OpenAPI
docs settings.
* **cors_config** - If [CORSConfig](../configurations/cors.md) is set it will enable the CORS built-in middleware.
* **static_files_config** - If [StaticFilesConfig](../configurations/staticfiles.md) is set, it will enable the
application static files configuration.
* **template_config** - If [TemplateConfig](../configurations/template.md) is set it will enable the template
engine from the configuration object.
* **session_config** - If [SessionConfig](../configurations/session.md) is set it will enable the session
built-in middleware.
* **response_class** - Custom subclass of [Response](../responses.md) to be used as application application response
class.
* **response_cookies** - List of [cookie](../datastructures.md) objects.
* **response_headers** - Mapping dictionary of header objects.
* **scheduler_class** - A [scheduler]('../scheduler/scheduler.md') class used for the application tasks. Defaults to
`AsyncIOScheduler`.
* **scheduler_tasks** - A python dictionary with key and pair values as strings mapping the [scheduler tasks](../scheduler/scheduler.md).
* **scheduler_configurations** - A python dictionary with key and pair values as strings mapping the
extra configuations of [scheduler tasks](../scheduler/handler.md).
* **enable_scheduler** - Flag indicating if the appliaction `scheduler` should be enabled or not. Defaults to `False`.
* **timezone** - The application default timezone. Defaults to `UTC`.
* **on_shutdown** - A list of callables to run on application shutdown. Shutdown handler callables do not take any
arguments, and may be be either standard functions, or async functions.

* **on_startup** - A list of callables to run on application startup. Startup handler callables do not take any
arguments, and may be be either standard functions, or async functions.
* **lifepan** - The lifespan context function is a newer style that replaces on_startup / on_shutdown handlers.
Use one or the other, not both.
* **tags** - List of tags to include in the OpenAPI schema.
* **include_in_schema** - Boolean flag to indicate if should be schema included or not.
* **deprecated** - Boolean flag for deprecation. Used for OpenAPI.
* **security** - Security definition of the application. Used for OpenAPI.
* **enable_openapi** - Flag to enable/disable OpenAPI docs. It is enabled by default.
* **redirect_slashes** - Flag to enable/disable redirect slashes for the handlers. It is enabled by default.

## Application settings

Settings are another way of controlling the parameters passed to the
[Esmerald object when instantiating](#instantiating-the-application). Check out the [settings](./settings.md) for
more details and how to use it to power up your application.

To access the application settings there are different ways:

=== "Within the application request"

    ```python hl_lines="6"
    {!> ../docs_src/application/settings/within_app_request.py!}
    ```

=== "From the global settings"

    ```python hl_lines="1 6"
    {!> ../docs_src/application/settings/global_settings.py!}
    ```

=== "From the conf settings"

    ```python hl_lines="2 7"
    {!> ../docs_src/application/settings/conf_settings.py!}
    ```

### State and application instance

You can store arbitraty extra state on the application instance using the [State](../datastructures.md) instance.

Example:

```python hl_lines="6"
{!> ../docs_src/application/others/app_state.py!}
```

## Accessing the application instance

The application instance can be access via `request` when it is available.

Example:

```python hl_lines="6"
{!> ../docs_src/application/others/access_app_instance.py!}
```

## Accessing the state from the application instance

The state can be access via `request` when it is available.

Example:

```python hl_lines="7 11"
{!> ../docs_src/application/others/access_state_from_app.py!}
```

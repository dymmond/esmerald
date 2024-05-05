# OpenAPIConfig

OpenAPIConfig is a simple configuration with basic fields for the auto-generated documentation from Esmerald.

Prior to version 2, there were two pieces for the documentation but now it is simplified with a simple
one.

!!! Tip
    More information about
    <a href="https://swagger.io/" target='_blank'>OpenAPI</a>.

You can create your own OpenAPIConfig and populate all the variables needed or you can simply
override the settings attributes and allow Esmerald to handle the configuration on its own. It
is up to you.

!!! Warning
    When passing OpenAPI attributes via instantiation, `Esmerald(docs_url='/docs/swagger',...)`,
    those will always be used over the settings or custom configuration.

## OpenAPIConfig and application

The `OpenAPIConfig` contains a bunch of simple fields that are needed to serve the documentation
and those can be easily overwritten.

Currently, by default, the URL for the documentation are:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.
* **Stoplight** - `/docs/elements`.

## Parameters

All the parameters and defaults are available in the [OpenAPIConfig Reference](../../references/configurations/openapi.md).

### How to use or create an OpenAPIConfig

It is very simple actually.

```python hl_lines="4 12"
{!> ../docs_src/configurations/openapi/example1.py !}
```

This will create your own `OpenAPIConfig` and pass it to the Esmerald application but what about changing the current
default `/docs` path?

Let's use an example for clarification.

```python
{!> ../docs_src/configurations/openapi/apiview.py !}
```

From now on the url to access `swagger`, `redoc` and `stoplight` will be:

* **Swagger** - `/another-url/swagger`.
* **Redoc** - `/another-url/redoc`.
* **Stoplight** - `/another-url/stoplight`.

## OpenAPIConfig and the application settings

As per normal Esmerald standard of configurations, it is also possible to enable the OpenAPI configurations via
settings.

```python
{!> ../docs_src/configurations/openapi/settings.py !}
```

Start the server with your custom settings.

```shell
ESMERALD_SETTINGS_MODULE=AppSettings uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

# OpenAPIConfig

OpenAPIConfig is a simple configuration with basic fields for the auto-genmerated documentation from Esmerald.

Prior to version 2, there were two pieces for the documentation but now it is simplified with a simple
one.

* [OpenAPIConfig](#openapiconfig)

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

The `OpenAPIConfig` contains a bunch of simple fields that are needed to to serve the documentation
and those can be easily overwritten.

Currently, by default, the URL for the documentation are:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.

## Parameters

This are the parameters needed for the OpenAPIConfig if you want to create your own configuration.

* **title** - Title of the API documentation.

    <sup>Default: `Esmerald title`</sup>

* **version** - The version of the API documentation.

    <sup>Default: `Esmerald version`</sup>

* **contact** - API contact information. This is an OpenAPI schema contact, meaning, in a dictionary format compatible
with OpenAPI or an instance of `openapi_schemas_pydantic.v3_1_0.contact.Contact`.

    <sup>Default: `Esmerald contact`</sup>

* **description** - API documentation description.

    <sup>Default: `Esmerald description`</sup>

* **terms_of_service** - URL to a page that contains terms of service.

    <sup>Default: `None`</sup>

* **license** - API Licensing information. This is an OpenAPI schema licence, meaning,
in a dictionary format compatible with OpenAPI or an instance of
`openapi_schemas_pydantic.v3_1_0.license.License`.

    <sup>Default: `None`</sup>

* **servers** - A python list with dictionary compatible with OpenAPI specification.

    <sup>Default: `[{"url": "/"}]`</sup>

* **summary** - Simple summary text.

    <sup>Default: `Esmerald summary`</sup>

* **security** - API Security requirements information. This is an OpenAPI schema security, meaning,
in a dictionary format compatible with OpenAPI or an instance of
`openapi_schemas_pydantic.v3_1_0.security_requirement.SecurityScheme`

    <sup>Default: `None`</sup>

* **tags** - A list of OpenAPI compatible `Tag` information. This is an OpenAPI schema tags, meaning,
in a dictionary format compatible with OpenAPI or an instance of `openapi_schemas_pydantic.v3_1_0.server.Server`.

    <sup>Default: `None`</sup>

* **root_path_in_servers** - A Flag indicating if the root path should be included in the servers.

    <sup>Default: `True`</sup>

* **openapi_url** - URL of the openapi.json.

    <sup>Default: `/openapi.json`</sup>

    !!! Danger
        Be careful when changing this one.

* **redoc_url** - URL where the redoc should be served.

    <sup>Default: `/docs/redoc`</sup>

* **swagger_ui_oauth2_redirect_url** - URL to serve the UI oauth2 redirect.

    <sup>Default: `/docs/oauth2-redirect`</sup>

* **redoc_js_url** - URL of the redoc JS.

    <sup>Default: `https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js`</sup>

* **redoc_favicon_url** - URL for the redoc favicon.

    <sup>Default: `https://esmerald.dev/statics/images/favicon.ico`</sup>

* **swagger_ui_init_oauth** - Python dictionary format with OpenAPI specification for the swagger
init oauth.

    <sup>Default: `None`</sup>

* **swagger_ui_parameters** - Python dictionary format with OpenAPI specification for the swagger ui
parameters.

    <sup>Default: `None`</sup>

* **swagger_js_url** - URL of the swagger JS.

    <sup>Default: `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`</sup>

* **swagger_css_url** - URL of the swagger CSS.

    <sup>Default: `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css`</sup>

* **swagger_favicon_url** - URL of the favicon for the swagger.

    <sup>Default: `https://esmerald.dev/statics/images/favicon.ico`</sup>


### How to use or create an OpenAPIConfig

It is very simple actually.

```python hl_lines="4 11"
{!> ../docs_src/configurations/openapi/example1.py!}
```

This will create your own `OpenAPIConfig` and pass it to the Esmerald application but what about changing the current
default `/docs` path?

Let's use a an example for clarification.

```python
{!> ../docs_src/configurations/openapi/apiview.py!}
```

From now on the url to access the `swagger` and `redoc` will be:

* **Swagger** - `/another-url/swagger`.
* **Redoc** - `/another-url/redoc`.

## OpenAPIConfig and the application settings

As per normal Esmerald standard of configurations, it is also possible to enable the OpenAPI configurations via
settings.

```python
{!> ../docs_src/configurations/openapi/settings.py!}
```

!!! Warning
    We did import the `MyOpenAPIView` inside the property itself and the reason for it is to avoid import errors
    or any `mro` issues. Since the app once starts runs the settings once, there is no problem since it will not
    reconfigure on every single request.

Start the server with your custom settings.

```shell
ESMERALD_SETTINGS_MODULE=AppSettings uvicorn src:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

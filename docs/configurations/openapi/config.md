# OpenAPIConfig

OpenAPIConfig is a simple configuration with basic fields for the auto-genmerated documentation from Esmerald.

Prior to version 2, there were two pieces for the documentation but now it is simplified with a simple
one.

* [OpenAPIConfig](#openapiconfig)

!!! Tip
    More information about
    <a href="https://swagger.io/" target='_blank'>OpenAPI</a>.

You can create your own OpenAPIConfig or simply

## OpenAPIConfig and application

The `OpenAPIConfig` contains a bunch of simple fields that are needed to to serve the documentation
and those can be easily overwritten.

Currently, by default, the URL for the documentation are:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.

## Parameters

* **create_examples** - Generates doc examples.

    <sup>Default: `False`</sup>

* **openapi_apiview** - The [OpenAPIView](./apiview.md) serving the docs.

    <sup>Default: `OpenAPIView`</sup>

* **title** - Title of the API documentation.

    <sup>Default: `Esmerald title`</sup>

* **version** - The version of the API documentation.

    <sup>Default: `Esmerald version`</sup>

* **contact** - API contact information. This is an OpenAPI schema contact, meaning, in a dictionary format compatible
with OpenAPI or an instance of `openapi_schemas_pydantic.v3_1_0.contact.Contact`.

    <sup>Default: `Esmerald contact`</sup>

* **description** - API documentation description.

    <sup>Default: `Esmerald description`</sup>

* **external_docs** - Links to external documentation. This is an OpenAPI schema external documentation, meaning,
in a dictionary format compatible with OpenAPI or an instance of
`openapi_schemas_pydantic.v3_1_0.external_documentation.ExternalDocumentation`.

    <sup>Default: `None`</sup>

* **license** - API Licensing information. This is an OpenAPI schema licence, meaning,
in a dictionary format compatible with OpenAPI or an instance of
`openapi_schemas_pydantic.v3_1_0.license.License`.

    <sup>Default: `None`</sup>

* **security** - API Security requirements information. This is an OpenAPI schema security, meaning,
in a dictionary format compatible with OpenAPI or an instance of
`openapi_schemas_pydantic.v3_1_0.security_requirement.SecurityScheme`

    <sup>Default: `None`</sup>

* **components** - A list of OpenAPI compatible `Server` information. OpenAPI specific dictionary or an instance of
`openapi_schemas_pydantic.v3_10_0.components.Components`

    <sup>Default: `None`</sup>

* **summary** - Simple summary text.

    <sup>Default: `Esmerald summary`</sup>

* **tags** - A list of OpenAPI compatible `Tag` information. This is an OpenAPI schema tags, meaning,
in a dictionary format compatible with OpenAPI or an instance of `openapi_schemas_pydantic.v3_1_0.server.Server`.

    <sup>Default: `None`</sup>

* **terms_of_service** - URL to a page that contains terms of service.

    <sup>Default: `None`</sup>

* **use_handler_docstrings** - Flag enabling to read the information from a [handler](../../routing/handlers.md)
docstring if no description is provided.

    <sup>Default: `False`</sup>

* **webhooks** - A mapping of key to either an OpenAPI `PathItem` or an OpenAPI `Reference` instance. Both PathItem and
Reference are in a dictionary format compatible with OpenAPI or an instance of
`openapi_schemas_pydantic.v3_1_0.path_item.PathItem` or `openapi_schemas_pydantic.v3_1_0.reference.Reference`.

    <sup>Default: `False`</sup>

* **root_schema_site** - Static schema generator to use for the "root" path of `/schema/`.

    <sup>Default: `redoc`</sup>

* **enabled_endpoints** - A set of the enabled documentation sites and schema download endpoints.

    <sup>Default: `{"redoc", "swagger", "elements", "openapi.json", "openapi.yaml"}`</sup>

### How to use or create an OpenAPIConfig

It is very simple actually.

```python hl_lines="4 11"
{!> ../docs_src/configurations/openapi/example1.py!}
```

This will create your own `OpenAPIConfig` and pass it to the Esmerald application but what about changing the current
default `/docs` path?

You will need an [OpenAPIView](./apiview.md) to make it work.

Let's use a an example for clarification.

```python title='myapp/openapi/views.py'
{!> ../docs_src/configurations/openapi/apiview.py!}
```

Then you need to add the new APIView to your OpenAPIConfig.

```python title='src/app.py'
{!> ../docs_src/configurations/openapi/example2.py!}
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

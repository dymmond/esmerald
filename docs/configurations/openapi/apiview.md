# OpenAPIView

This is a very special object that manages everything `OpenAPI` related documentation.

In simple terms, the OpenAPIView simply creates the handlers for the `swagger` and `redoc` and registers those
within your application routes.

```python title='myapp/openapi/views.py'
{!> ../docs_src/configurations/openapi/apiview.py!}
```

## Parameters

There are a few internal parameteres being used by Esmerald and we **strongly recommend not to mess up with them
unless you are confortable with everything** and only override the `path` parameter when needed.

* **path** - The path prefix for the documentation.

    <sup>Default: `/docs`</sup>

## The documentation URLs

Esmerald OpenAPI documentation by default will use `/docs` prefix to access the OpenAPI application documentation.

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.

### Overriding the default path

Let's have another look at the example given above.

```python title='myapp/openapi/views.py'
{!> ../docs_src/configurations/openapi/apiview.py!}
```

Since the path prefix became `/another=url` you can now access the documentation via:

* **Swagger** - `/another-url/swagger`.
* **Redoc** - `/another-url/redoc`.

!!! Tip
    The OpenAPI documentation works really well natively and we advise, once again, to be careful when overriding
    parameteres other than **`/path`**.

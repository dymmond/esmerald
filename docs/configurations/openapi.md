# OpenAPIConfig

OpenAPIConfig is a simple configuration with basic fields for the auto-genmerated documentation from Esmerald.
Allows to decide for instance, wich `path` you want to serve the documentation. Defaults to `docs`.

!!! Tip
    More information about OpenAPI
    <a href="https://swagger.io/" target='_blank'>here</a>.

## OpenAPIConfig and application

To use the OpenAPIConfig in an application instance.

```python hl_lines="4-5 8"
{!> ../docs_src/configurations/csrf/example1.py!}
```

Another example

```python hl_lines="4-5 8"
{!> ../docs_src/configurations/openapi/example2.py!}
```

## Parameters

* **secret** - The string used for the encryption/decryption. We advise to use the same secret as the one in the
settings to make it consistent.
* **cookie_name** - CSRF cookie name.

    <sup>Default: `csrftoken`</sup>

* **cookie_path** - CSRF cookie path.

    <sup>Default: `/`</sup>

* **header_name** - Header expected in the requests.

    <sup>Default: `X-CSRFToken`</sup>

* **cookie_secure** - Boolean flag when enabled sets `Secure` of the cookie.

    <sup>Default: `False`</sup>

* **cookie_httponly** - Boolean flag when enabled sets the cookie to be httpsOnly.

    <sup>Default: `False`</sup>

* **cookie_samesite** - Sets the `SameSite` attribute of the cookie.

    <sup>Default: `lax`</sup>

* **cookie_domain** - The hosts that can receive the cookie.

    <sup>Default: `lax`</sup>

* **safe_methods** - A set of allowed safe methods that can set the cookie.

    <sup>Default: `{"GET", "HEAD"}`</sup>

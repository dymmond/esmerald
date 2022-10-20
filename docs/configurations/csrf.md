# CSRFConfig

CSRF extends for Cross-Site Request Forgery and it's one of the built-in middlewares of Esmerald.
When a CSRFConfig object is passed to an application instance, it will automatically start the `CSRFMiddleware`.

!!! Tip
    More information about CSRF
    <a href="https://owasp.org/www-community/attacks/csrf" target='_blank'>here</a>.

## CSRFConfig and application

To use the CSRFConfig in an application instance.

```python hl_lines="4-5 8"
{!> ../docs_src/configurations/csrf/example1.py!}
```

Another example

```python hl_lines="4 7"
{!> ../docs_src/configurations/csrf/example2.py!}
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

## CSRFConfig and application settings

The CSRFConfig can be done directly via [application instantiation](#csrfconfig-and-application) but also via settings.

```python
{!> ../docs_src/configurations/csrf/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

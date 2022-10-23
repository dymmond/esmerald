# CORSConfig

CORS extends for Cross-Origin Resource Sharing and it is one of the built-in middlewares of Esmerald.
When a CORSConfig object is passed to an application instance, it will automatically start the `CORSMiddleware`.

!!! Tip
    More information about CORS
    <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS" target='_blank'>here</a>.

!!! Check
    If the `allowed_hosts` is provided via application instance or settings, it will automatically start the
    `TrustedHostMiddleware`.

## CORSConfig and application

To use the CORSConfig in an application instance.

```python hl_lines="4 7"
{!> ../docs_src/configurations/cors/example1.py!}
```

Another example

```python hl_lines="4-6 9"
{!> ../docs_src/configurations/cors/example2.py!}
```

## Parameters

* **allow_origins** - A list of strings of allowed hosts. It can be used `'*'` in any part of the path. 
E.g.: `example.*.org.

    <sup>Default: `['*']`</sup>
    <sup>Default: `Access-Control-Allow-Origin`</sup>

* **allow_methods** - List of allowed HTTP methods.

    <sup>Default: `['*']`</sup>
    <sup>Header: `Access-Control-Allow-Methods`</sup>

* **allow_headers** - List of allowed headers.

    <sup>Default: `['*']`</sup>
    <sup>Header: `Access-Control-Allow-Headers`</sup>

* **allow_credentials** - Boolean flag enabling/disabling the credentials header.

    <sup>Default: `False`</sup>
    <sup>Header: `Access-Control-Allow-Credentials`</sup>

* **allow_origin_regex** - Regex to match origins.

    <sup>Default: `None`</sup>

* **expose_headers** - List of headers exposed via `Access-Control-Expose-Headers`.

    <sup>Default: `[]`</sup>

* **max_age** - Response TTL in seconds.

    <sup>Default: `600`</sup>
    <sup>Header: `Access-Control-Max-Age`</sup>

## CORSConfig and application settings

The CORSConfig can be done directly via [application instantiation](#corsconfig-and-application) but also via settings.

```python
{!> ../docs_src/configurations/cors/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

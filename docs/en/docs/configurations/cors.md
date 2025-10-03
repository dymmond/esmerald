# CORSConfig

CORS extends for Cross-Origin Resource Sharing and it is one of the built-in middlewares of Ravyn.
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
{!> ../../../docs_src/configurations/cors/example1.py!}
```

Another example

```python hl_lines="4-6 9"
{!> ../../../docs_src/configurations/cors/example2.py!}
```

## Parameters

All the parameters and defaults are available in the [CORSConfig Reference](../references/configurations/cors.md).

## CORSConfig and application settings

The CORSConfig can be done directly via [application instantiation](#corsconfig-and-application) but also via settings.

```python
{!> ../../../docs_src/configurations/cors/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Ravyn** instance.

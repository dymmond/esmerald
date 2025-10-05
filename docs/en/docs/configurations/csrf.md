# CSRFConfig

CSRF extends for Cross-Site Request Forgery and it is one of the built-in middlewares of Ravyn.
When a CSRFConfig object is passed to an application instance, it will automatically start the `CSRFMiddleware`.

!!! Tip
    More information about CSRF
    <a href="https://owasp.org/www-community/attacks/csrf" target='_blank'>here</a>.

## CSRFConfig and application

To use the CSRFConfig in an application instance.

```python hl_lines="4-5 8"
{!> ../../../docs_src/configurations/csrf/example1.py!}
```

Another example

```python hl_lines="4 7"
{!> ../../../docs_src/configurations/csrf/example2.py!}
```

## Parameters

All the parameters and defaults are available in the [CSRFConfig Reference](../references/configurations/csrf.md).

## CSRFConfig and application settings

The CSRFConfig can be done directly via [application instantiation](#csrfconfig-and-application) but also via settings.

```python
{!> ../../../docs_src/configurations/csrf/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Ravyn** instance.

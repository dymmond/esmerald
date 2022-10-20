# SessionConfig

SessionConfig is simple set of configurations that when passed enables the built-in middleware of Esmerald.
When a SessionConfig object is passed to an application instance, it will automatically start the `SessionMiddleware`.

!!! Tip
    More information about HTTP Sessions
    <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Session" target='_blank'>here</a>.

## SessionConfig and application

To use the SessionConfig in an application instance.

```python hl_lines="4 7"
{!> ../docs_src/configurations/session/example1.py!}
```

Another example

```python hl_lines="4-5 8"
{!> ../docs_src/configurations/session/example2.py!}
```

## Parameters

* **secret_key** - The string used for the encryption/decryption. We advise to use the same secret as the one in the
settings to make it consistent.

* **path** - The path for the cookie.

    <sup>Default: `/`</sup>

* **session_cookie** - The name for the session cookie.

    <sup>Default: `session`</sup>

* **max_age** - The number in seconds until the cookie expires.

    <sup>Default: `15552000`. `60 sec x 60min x 24h x 180days = 15552000 seconds` </sup>

* **https_only** - Boolean if set enforces the session cookie to be httpsOnly.

    <sup>Default: `False`</sup>

* **same_site** - Level of restriction for the session cookie. 
<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite" target="_blank">
More on this</a>.

    <sup>Default: `lax`</sup>

## SessionConfig and application settings

The SessionConfig can be done directly via [application instantiation](#sessionconfig-and-application) but also via settings.

```python
{!> ../docs_src/configurations/session/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

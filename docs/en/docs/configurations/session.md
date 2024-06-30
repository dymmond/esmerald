# SessionConfig

SessionConfig is simple set of configurations that when passed enables the built-in middleware of Esmerald.
When a SessionConfig object is passed to an application instance, it will automatically start the `SessionMiddleware`.

!!! Tip
    More information about HTTP Sessions
    <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Session" target='_blank'>here</a>.

## SessionConfig and application

To use the SessionConfig in an application instance.

```python hl_lines="4 7"
{!> ../../../docs_src/configurations/session/example1.py!}
```

Another example

```python hl_lines="4-5 8"
{!> ../../../docs_src/configurations/session/example2.py!}
```

## Parameters

All the parameters and defaults are available in the [SessionConfig Reference](../references/configurations/session.md).

## SessionConfig and application settings

The SessionConfig can be done directly via [application instantiation](#sessionconfig-and-application) but also via settings.

```python
{!> ../../../docs_src/configurations/session/settings.py!}
```

This will make sure you keep the settings clean, separated and without a bloated **Esmerald** instance.

## Esmerald Sessions

If you don't want to use the built-in session configuration and if you fancy a more custom way of handling the sessions
with Esmerald, there is an official package
[Esmerald Sessions](https://esmerald-sessions.dymmond.com/) that can help you with that including the middleware.

# Third Party Packages & Integrations

Esmerald being an ASGI framework that also support WSGI through [WSGIMiddleware](./wsgi.md) also allows the integrations
with third parties and their packages and frameworks.

## GraphQL

Natively Esmerald does not integrate GraphQL, at least not for now. Instead there already available awesome
working solutions built by great minds.

### <a href="https://ariadnegraphql.org/docs/asgi" target="_blank">Ariadne</a>

Great framework with great documentation and great examples how to use it. Currently they also have an integration
with Starlette and that also means **Esmerald**. Their example is with Starlette but here we also provide an example
for Esmerald.

```python
{!> ../docs_src/external_packages/ariadne.py !}
```

The documentation can be found <a href="https://ariadnegraphql.org/docs/intro" target="_blank">here</a>.

### Ariadne version 0.16.1

!!! Warning
    By the time of this writing, `Starlette` was in the version `0.21.0`.
    Due to the nature of `Esmerald`, when installing `Ariadne` it will install a lower version and this will
    conflict with **Esmerald**. After you install `ariadne` make sure you reinstall `Starlette>=0.21.0`.
    Until a new version of the package comes out supporting the latest from Starlette, this is the workaround.

## [Esmerald Sessions](https://esmerald-sessions.dymmond.com/)

Manages sessions for Esmerald using Redis, Memcache or any custom backend.


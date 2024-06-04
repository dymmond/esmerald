# Third Party Packages & Integrations

Esmerald being an ASGI framework that also support WSGI through [WSGIMiddleware](./wsgi.md) also allows the integrations
with third parties and their packages and frameworks.

## GraphQL

Natively Esmerald does not integrate GraphQL, at least not for now. Instead there already available awesome
working solutions built by great minds.

### <a href="https://ariadnegraphql.org/docs/asgi" target="_blank">Ariadne</a>

Great framework with great documentation and great examples how to use it.

```python
{!> ../docs_src/external_packages/ariadne.py !}
```

The documentation can be found <a href="https://ariadnegraphql.org/docs/intro" target="_blank">here</a>.

## [Esmerald Sessions](https://esmerald-sessions.dymmond.com/)

Manages sessions for Esmerald using Redis, Memcache or any custom backend.

### Esmerald Simple JWT

Do you need to implement a JWT access with Esmerald and you don't want to spend a lot of timme configuring
and designing the how to? Dymmond provides you with an out of the box solution for that with
Esmerald Simple JWT.

## [Esmerald Simple JWT](https://esmerald-simple-jwt.dymmond.com/)

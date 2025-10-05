# Third Party Packages

Ravyn being an ASGI framework that also support WSGI through [WSGIMiddleware](./wsgi.md) also allows the integrations
with third parties and their packages and frameworks.

## GraphQL

Natively Ravyn does not integrate GraphQL, at least not for now. Instead there already available awesome
working solutions built by great minds.

### <a href="https://ariadnegraphql.org/docs/asgi" target="_blank">Ariadne</a>

Great framework with great documentation and great examples how to use it.

```python
{!> ../../../docs_src/external_packages/ariadne.py !}
```

The documentation can be found <a href="https://ariadnegraphql.org/docs/intro" target="_blank">here</a>.

### Ravyn Simple JWT

Do you need to implement a JWT access with Ravyn and you don't want to spend a lot of timme configuring
and designing the how to? Dymmond provides you with an out of the box solution for that with
Ravyn Simple JWT (Works)

## [Ravyn Simple JWT](https://ravyn-simple-jwt.dymmond.com/)

## [Ravyn using the scheduler](https://github.com/dymmond/scheduler-example)

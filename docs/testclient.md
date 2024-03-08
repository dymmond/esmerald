# Test Client

Esmerald comes with a test client for your application tests. It is not mandatory use it as every application and
development team has its own way of testing it but just in case, it is provided.

## Requirements

This section requires the esmerald testing suite to be installed. You can do it so by running:

```shell
$ pip install esmerald[test]
```

## API Reference

Check the [API Reference for the test client](./references/test-client.md) to understand more.

## The test client

```python
{!> ../docs_src/testclient/example1.py !}
```

The test client is very similar to its original as it extends it and adds extra unique and specifics for `Esmerald`
and therefore the same examples and use cases will work.

You can use any of the `httpx` standard API like authentication, session cookies and file uploads.

```python
{!> ../docs_src/testclient/example2.py !}
```

And like Lilya, the same example to send files with `EsmeraldTestClient`.

```python
{!> ../docs_src/testclient/example3.py !}
```

`httpx` is a great library created by the same author of `Django Rest Framework`.

!!! Info
    By default the EsmeraldTestClient raise any exceptions that occur in the application.
    Occasionally you might want to test the content of 500 error responses, rather than allowing client to raise the
    server exception. In this case you should use `client = EsmeraldTestClient(app, raise_server_exceptions=False)`.

## Lifespan events

!!! Note
    Esmerald supports all the lifespan events available and therefore `on_startup`, `on_shutdown` and `lifespan` are
    also supported by `EsmeraldTestClient` **but** if you need to test these you will need to run `EsmeraldTestClient`
    as a context manager or otherwise the events will not be triggered when the `EsmeraldTestClient` is instantiated.

The framework also brings a ready to use functionality to be used as context manager for your tests.

### Context manager `create_client`

This function is prepared to be used as a context manager for your tests and ready to use at any given time.

```python
{!> ../docs_src/testclient/example4.py !}
```

The tests work with both `sync` and `async` functions.

!!! info
    The example above is used to also show the tests can be as complex as you desire and it will work with the
    context manager.

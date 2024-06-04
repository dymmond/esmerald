# WSGI frameworks

Did you know because of the awesome work from [a2wsgi](https://github.com/abersheeran/a2wsgi)
added to the simplicity of Esmerald you can integrate any wsgi framework (Flask, Django...)?

Yes, that's right, you can now smoothly move to Esmerald without rewriting your old applications from the scratch,
actually, you can reuse them directly within Esmerald, even another Esmerald running inside another Esmerald,
an *Esmeraldception*.

## WSGIMiddleware

Using this middleware is very simple, let's use Flask as example since it is very fast to spin-up a Flask service
compared to other giants like Django.

=== "Simple Routing"

    ```python hl_lines="1 6 9 24"
    {!> ../docs_src/wsgi/simple_routing.py!}
    ```

=== "Nested Routing"

    ```python hl_lines="1 6 9 26"
    {!> ../docs_src/wsgi/nested_routing.py!}
    ```

=== "Complex Routing"

    ```python hl_lines="1 6-7 10 16 37 51"
    {!> ../docs_src/wsgi/complex_routing.py!}
    ```

=== "Multiple Flask"

    ```python hl_lines="1 6-7 10 22 33-34"
    {!> ../docs_src/wsgi/multiple.py!}
    ```

=== "Esmerald"

    ```python hl_lines="1 6-7 10 22 31-32 36"
    {!> ../docs_src/wsgi/esmerald.py!}
    ```

=== "ChildEsmerald"

    ```python hl_lines="1 6-7 10 22 31-32 36"
    {!> ../docs_src/wsgi/childesmerald.py!}
    ```

You already get the idea, the integrations are endeless!

## Verify it

With all of examples from before, you can now verify that the integrations are working.

The paths pointing to the `WSGIMiddleware` will be handled by Flask and the rest is handled by **Esmerald**,
including the Esmerald inside another Esmerald.

If you run the endpoint handled by Flask:

* `/flask` - From simple routing.
* `/flask` - From nested routing.
* `/internal/flask` and `/external/second/flask` - From complex routing.
* `/flask` and `/second/flask` - From multiple flask apps.
* `/esmerald/flask` and `/esmerald/second/flask` - From inside another Esmerald

You will see the response:

```shell
Hello, Esmerald from Flask!
```

Accessing any `Esmerald` endpoint:

* `/home/esmerald` - From simple routing.
* `/home/esmerald` - From complex routing.
* `/home/esmerald` - From nested routing.
* `/home/esmerald` - From multiple flask apps.
* `/esmerald/home/esmerald` - From inside another Esmerald

```json
{
    "name": "esmerald"
}
```

## WSGI and Esmerald OpenAPI

Only apps that are inherited from [Esmerald](./application/applications.md)
or [ChildEsmerald](./routing/router.md#child-esmerald-application) will be showing
in the OpenAPI documentation. This is for compatibility purposes only and **does not affect** the internal
routing.

WSGI integrations and all the urls associated still work.

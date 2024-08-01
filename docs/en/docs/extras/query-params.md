# Query Parameters

It is very common to simply want to declare some query parameters in your controllers. Sometimes those are also used
as filters for a given search or simply extra parameters in general.

## What are query parameters in Esmerald?

Query parameters are those parameters that are not part of the path parameters and therefore those are automatically
injected as `query` parameters for you.

```python
{!> ../../../docs_src/extras/query/example1.py !}
```

As you can see, the query is a key-pair value that goes after the `?` in the URL and seperated by a `&`.

Applying the previous example, it would look like this:

```shell
http://127.0.0.1/users?skip=1&limit=5
```

The previous url will be translated as the following `query_params`:

- `skip`: with a value of 1.
- `limit`: with a value of 5.

Since they are an integral part of the URL, it will automatically populate the parameters of the function that corresponds
each value.

## Declaring defaults

Query parameters are not by design, part of a fixed URL path and that also means they can assume the following:

- They can have defaults, like `skip=1` and `limit=5`.
- They can be `optional`.

In the previous example, the URL had already defaults for `skip` and `limit` and the corresponding typing as per requirement
of Esmerald but what if we want to make them optional?

There are different ways of achieving that, using the `Optional` or `Union`.

!!! Tip
    from Python 3.10+ the `Union` can be replaced with `|` syntax.


=== "Using Optional"

    ```python
    {!> ../../../docs_src/extras/query/example_optional.py !}
    ```

=== "Using Union"

    ```python
    {!> ../../../docs_src/extras/query/example_union.py !}
    ```

!!! Check
    Esmerald is intelligent enough to understand what is a `query param` and what is a `path param`.

Now we can call the URL and ignore the `q` or call it when needed, like this:

**Without query params**

```shell
http://127.0.0.1/users/1
```

**With query params**

```shell
http://127.0.0.1/users/1?q=searchValue
```

## Query and Path parameters

Since Esmerald is intelligent enough to distinguish path parameters and query parameters automatically, that also means
you can have multiple of both combined.

!!! Warning
    You can't have a query and path parameters with the same name as in the end, it is still Python parameters being
    declared in a function.

```python
{!> ../../../docs_src/extras/query/example_combined.py !}
```

## Required parameters

When you declare a `query parameter` **without a default** and **without being optional** when you call the URL
it will raise an error of missing value for the corresponding.

```python
{!> ../../../docs_src/extras/query/example_mandatory.py !}
```

If you call the URL like this:

```
http://127.0.0.1/users
```

It will raise an error of missing value, something like this:

```json
{
  "detail": "Validation failed for <URL> with method GET.",
  "errors": [
    {
      "type": "int_type",
      "loc": [
        "limit"
      ],
      "msg": "Input should be a valid integer",
      "input": null,
      "url": "https://errors.pydantic.dev/2.8/v/int_type"
    }
  ]
}
```

Which means, you need to call with the declared parameter, like this, for example:

```shell
http://127.0.0.1/users?limit=10
```

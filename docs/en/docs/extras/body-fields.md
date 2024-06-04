# The Body

Sometimes you might want to pass extra information into your handler and possibly customize the OpenAPI
documentation for the request body schema or how to control its validation.

The simplest way is by importing the `Body` object from Esmerald.

```python hl_lines="13"
{!> ../docs_src/extras/body/body_object.py !}
```

## URL Enconded

What if a payload needs to be sent with a specific format? For instance a form?

As [explained here](./request-data.md#request-data), the handler is expecting a `data` field declared and from there
you can pass more details about the body.

```python
{!> ../docs_src/extras/body/url_encoded.py !}
```

There are different `media_types` that can be used.

* `JSON` - application/json which happens to also be the default.
* `URL_ENCODED` - application/x-www-form-urlencoded
* `MULTI_PART` - multipart/form-data

All of those are standards in most of the frameworks out there.

**Another example**:

```python
{!> ../docs_src/extras/body/multipart.py !}
```

### Important

Since `Body` is Pydantic field (sort of), that also means you can specify for instance,
the other parameters to be evaluated.

You can check [the list of available parameters default](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.FieldInfo)
as well.

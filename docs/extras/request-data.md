# Request Data

In every application there will be times where sending a payload to the server will be needed.

Esmerald is prepared to handle those with ease and that is thanks to Pydantic.

## The `data` field

When sending a payload to the backend to be validated, the handler needs to have a `data` field declared. Without it,
it will not be possible to process the information and/or will not be recognised.

```python hl_lines="12"
{!> ../docs_src/extras/request_data/data_field.py !}
```

Fundamentally the `data` field is what holds the information about the sent payload data into the server.

The data can also be simple types such as `list`, `dict`, `str`. It does not necessarily mean you need to always use
pydantic models.

## Nested models

You can also do nested models for the `data` to be processed.

```python hl_lines="6 16 20"
{!> ../docs_src/extras/request_data/nested_models.py !}
```

The data expected to be sent to be validated is all required and expected with the following format:

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "address": {
        "zip_code": "90210",
        "country": "United States",
        "street": "Orange county street",
        "region": "California"
    }
}
```

You can nest as many models as you wish to nest as long as it is send in the right format.

## Mandatory fields

There are many ways to process and validate a field and also the option to make it non mandatory.

That can be achieved by using the typing `Optional` to make it not mandatory.

```python hl_lines="9-10 16"
{!> ../docs_src/extras/request_data/not_mandatory.py !}
```

The `address` is not mandatory to be send in the payload and therefore it can be done like this:

```json
{
    "name": "John",
    "email": "john.doe@example.com"
}
```

But you can also send the address and inside without the mandatory fields:

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "address": {
        "zip_code": "90210",
        "country": "United States"
    }
}
```

## Field validation

What about the field validation? What if you need to validate some of the data being sent to the backend?

Since Esmerald uses pydantic, you can take advantage of it.

```python hl_lines="9 11-12"
{!> ../docs_src/extras/request_data/validation.py !}
```

Since pydantic runs the validations internally, you will have the errors thrown if something is missing.

The expected payload would be:

```json
{
    "name": "John",
    "email": "john.doe@example.com",
    "hobbies": [
        "running",
        "swimming",
        "Netflix bing watching"
    ],
    "age": 18
}
```

## Custom field validation

You don't necessarily need to use the pydantic default validation for your fields. You can always apply one of your
own.

```python
{!> ../docs_src/extras/request_data/custom_validation.py !}
```

## Summary

* To process a payload it must have a `data` field declared in the handler.
* `data` can be any type, including pydantic models.
* Validations can be achieved by:
    * Using the `Field` from pydantic and automatic delegate the validations to it.
    * Using custom validations.
* To make a field non-mandatory you must use the `Optional`.

# Handling Forms in Esmerald

Esmerald provides a streamlined approach to handle form submissions, leveraging Python's data classes
and Pydantic models for data validation. The `Form` class in Esmerald simplifies the process of receiving
form data in your endpoints.

## Accessing the `Form` Class

To handle form data, import the `Form` class from Esmerald:

```python
from esmerald import Form
```


Alternatively, you can import it from the `params` module:

```python
from esmerald.params import Form
```


## Defining Form Data Structures

Esmerald allows you to define the structure of your form data using various Python constructs:

### 1. Using a Dictionary

Handle form data as a standard Python dictionary:

```python
from typing import Dict
from esmerald import Esmerald, Form, Gateway, post

@post("/create")
async def create_user(data: Dict[str, str] = Form()) -> Dict[str, str]:
    """
    Creates a user in the system and returns the received data.
    """
    return data

app = Esmerald(routes=[Gateway(handler=create_user)])
```


### 2. Using a Dataclass

Utilize Python's `dataclass` for form data:

```python
from dataclasses import dataclass
from esmerald import Esmerald, Form, Gateway, post

@dataclass
class User:
    name: str
    email: str

@post("/create")
async def create_user(data: User = Form()) -> User:
    """
    Creates a user in the system and returns the received data.
    """
    return data

app = Esmerald(routes=[Gateway(handler=create_user)])
```


### 3. Using a Pydantic Dataclass

Combine Pydantic's data validation with form handling:

```python
from pydantic.dataclasses import dataclass
from esmerald import Esmerald, Form, Gateway, post

@dataclass
class User:
    name: str
    email: str

@post("/create")
async def create_user(data: User = Form()) -> User:
    """
    Creates a user in the system and returns the received data.
    """
    return data

app = Esmerald(routes=[Gateway(handler=create_user)])
```


### 4. Using a Pydantic Model

Leverage Pydantic models for advanced data validation:

```python
from pydantic import BaseModel
from esmerald import Esmerald, Form, Gateway, post

class User(BaseModel):
    name: str
    email: str

@post("/create")
async def create_user(data: User = Form()) -> User:
    """
    Creates a user in the system and returns the received data.
    """
    return data

app = Esmerald(routes=[Gateway(handler=create_user)])
```


## Handling Form Data in Requests

When sending form data in a request, ensure the payload matches the expected structure.
For example, sending a JSON payload:

```json
{
    "name": "example",
    "email": "example@esmerald.dev"
}
```


Esmerald will automatically parse this JSON into the appropriate data structure based on your handler's
definition.

## Using Form as a Non-Data Field

Esmerald's `Form` can also be used for fields that are neither data nor payload:

```python
from esmerald import Esmerald, Form, Gateway, post

@post("/submit")
async def submit_form(data: Form = Form()) -> None:
    """
    Handles a form submission without specific data processing.
    """
    pass

app = Esmerald(routes=[Gateway(handler=submit_form)])
```

## Notes

- The `Form` class inherits from Pydantic's `Field`, allowing you to specify additional parameters for data
validation.

## Important

Since `Form` is derived from Pydantic's `Field`, you can utilize various validation parameters,
such as `min_length`, `max_length`, `regex`, and more, to enforce constraints on form fields.

---

By utilizing Esmerald's `Form` class, you can efficiently handle form submissions in a manner consistent with
modern Python web frameworks, ensuring clean and maintainable code.

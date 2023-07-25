from dataclasses import dataclass

import httpx

from esmerald import Esmerald, Form, Gateway, post


@dataclass
class User:
    name: str
    email: str


@post("/create")
async def create(data: User = Form()) -> User:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """
    return data


app = Esmerald(routes=[Gateway(handler=create)])

# Payload example
data = {"name": "example", "email": "example@esmerald.dev"}

# Send the request
httpx.post("/create", data=data)

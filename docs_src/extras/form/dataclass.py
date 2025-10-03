from dataclasses import dataclass

import httpx

from ravyn import Ravyn, Form, Gateway, post


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


app = Ravyn(routes=[Gateway(handler=create)])

# Payload example
data = {"name": "example", "email": "example@ravyn.dev"}

# Send the request
httpx.post("/create", data=data)

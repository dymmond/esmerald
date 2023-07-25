from typing import Any, Dict

import httpx

from esmerald import Esmerald, Form, Gateway, post


@post("/create")
async def create(data: Dict[str, str] = Form()) -> Dict[str, str]:
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

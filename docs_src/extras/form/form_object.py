from typing import Any, Dict

from esmerald import Esmerald, Form, Gateway, post


@post("/create")
async def create_user(data: Dict[str, Any] = Form()) -> None:
    """
    Creates a user in the system and does not return anything.
    Default status_code: 201
    """


app = Esmerald(routes=[Gateway(handler=create_user)])

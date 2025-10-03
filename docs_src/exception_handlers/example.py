from pydantic import BaseModel

from ravyn import Ravyn, Gateway, JSONResponse, post


class DataIn(BaseModel):
    id: int
    name: str


@post("/create")
async def create(data: DataIn) -> JSONResponse:
    # Simple validation to raise ValueError
    if data.id > 20:
        raise ValueError("The ID must be less than 20.")


app = Ravyn(routes=[Gateway(handler=create)])

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, JSONResponse, post


class DataIn(BaseModel):
    id: int
    name: str


@post("/create")
async def create(data: DataIn) -> JSONResponse:
    # Simple validation to raise ValueError
    if data.id > 20:
        raise ValueError("The ID must be less than 20.")


app = Esmerald(routes=[Gateway(handler=create)])

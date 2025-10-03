from pydantic import BaseModel, ValidationError

from ravyn import Ravyn, Gateway, JSONResponse, post
from ravyn.exception_handlers import pydantic_validation_error_handler, value_error_handler


class DataIn(BaseModel):
    id: int
    name: str


@post("/create")
async def create(data: DataIn) -> JSONResponse:
    # Simple validation to raise ValueError
    if data.id > 20:
        raise ValueError("The ID must be less than 20.")


app = Ravyn(
    routes=[Gateway(handler=create)],
    exception_handlers={
        ValueError: value_error_handler,
    },
)

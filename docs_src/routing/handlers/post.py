from pydantic import BaseModel

from ravyn import Ravyn, Gateway, post


class Item(BaseModel):
    sku: str
    name: str


@post(path="/create")
def create(data: Item) -> None:
    # Operations to create here
    ...


@post(path="/")
def another(name: str) -> str:
    return f"Another welcome, {name}!"


app = Ravyn(
    routes=[
        Gateway(handler=create),
        Gateway(path="/last/{name:str}", handler=another),
    ]
)

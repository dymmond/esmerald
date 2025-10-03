from pydantic import BaseModel

from ravyn import Ravyn, Gateway, post


class User(BaseModel):
    name: str
    email: str


@post("/create")
def create(data: User) -> User: ...


app = Ravyn(routes=[Gateway(handler=create)])

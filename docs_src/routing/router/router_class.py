from pydantic import BaseModel

from esmerald import Esmerald, Gateway, post


class User(BaseModel):
    name: str
    email: str


@post("/create")
def create(data: User) -> User:
    ...


app = Esmerald(routes=[Gateway(handler=create)])

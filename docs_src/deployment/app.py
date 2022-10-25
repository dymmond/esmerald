from typing import Union

from esmerald import Esmerald, Gateway, get


@get("/")
def home():
    return {"Hello": "World"}


@get("/users/{user_id}")
def read_user(user_id: int, q: Union[str, None] = None):
    return {"item_id": user_id, "q": q}


app = Esmerald(
    routes=[
        Gateway(handler=home),
        Gateway(handler=read_user),
    ]
)

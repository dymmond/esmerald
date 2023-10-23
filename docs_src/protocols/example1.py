from myapp.accounts import User
from pydantic import BaseModel
from saffier.exceptions import ObjectNotFound, SaffierException

from esmerald import Esmerald, Gateway, post


class UserModel(BaseModel):
    name: str
    email: str


@post("/create")
async def create(data: UserModel) -> None:
    try:
        await User.get(email=data.email, name=data.name)
    except ObjectNotFound:
        await User.create(email=data.email, name=data.name)
    except SaffierException:
        # raises an error here
        ...


app = Esmerald(routes=[Gateway(handler=create)])

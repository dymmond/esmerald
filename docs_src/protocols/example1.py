from myapp.accounts import User
from pydantic import BaseModel
from edgy.exceptions import ObjectNotFound, SaffierException

from ravyn import Ravyn, Gateway, post


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


app = Ravyn(routes=[Gateway(handler=create)])

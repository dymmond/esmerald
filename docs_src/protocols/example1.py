from esmerald import Esmerald, Gateway, post
from myapp.accounts import User
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, IntegrityError


class UserModel(BaseModel):
    name: str
    email: str


@post("/create")
async def create(data: UserModel) -> None:
    try:
        await User.get(email=data.email, name=data.name)
    except DoesNotExist:
        await User.create(email=data.email, name=data.name)
    except IntegrityError:
        # raises an error here
        ...


app = Esmerald(routes=[Gateway(handler=create)])

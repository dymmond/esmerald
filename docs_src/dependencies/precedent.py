from myapp.accounts.models import User
from saffier.exceptions import ObjectNotFound

from esmerald import Esmerald, Gateway, Inject, Injects, get


async def get_user_model() -> User:
    try:
        return await User.get(pk=1)
    except ObjectNotFound:
        return None


@get("/me", dependencies={"user": Inject(get_user_model)})
async def me(user: User = Injects()) -> str:
    return user.email


app = Esmerald(routes=[Gateway(handler=me)])

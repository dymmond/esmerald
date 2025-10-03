from myapp.accounts.models import User
from edgy.exceptions import ObjectNotFound

from ravyn import Ravyn, Gateway, Inject, Injects, get


async def get_user_model() -> User:
    try:
        return await User.get(pk=1)
    except ObjectNotFound:
        return None


@get("/me", dependencies={"user": Inject(get_user_model)})
async def me(user: User = Injects()) -> str:
    return user.email


app = Ravyn(routes=[Gateway(handler=me)])

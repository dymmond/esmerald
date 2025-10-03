from typing import Any
from ravyn import Ravyn, Gateway, Inject, get
from ravyn.injector import Factory


class UserDAO:
    def __init__(self, pool_size: int = 10, **kwargs: Any):
        self.db_url = kwargs.get("db_url", None)
        self.pool_size = pool_size


@get(
    "/users",
    dependencies={
        "user_dao": Inject(
            Factory(UserDAO, pool_size=20, db_url="sqlite://database.db"),
        )
    },
)
async def user_service(user_dao: UserDAO):
    return user_dao


app = Ravyn(routes=[Gateway(handler=user_service)])

from esmerald import Esmerald, Gateway, Inject, get
from esmerald.injector import Factory


class UserDAO:
    def __init__(self, db_url: str, pool_size: int = 10):
        self.db_url = db_url
        self.pool_size = pool_size


@get(
    "/users",
    dependencies={
        "user_dao": Inject(
            Factory(
                UserDAO,
                "sqlite://database.db",
                pool_size=20,
            )
        )
    },
)
async def user_service(user_dao: UserDAO):
    return user_dao


app = Esmerald(routes=[Gateway(handler=user_service)])

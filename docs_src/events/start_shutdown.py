from pydantic import BaseModel
from edgy import Database, Registry

from ravyn import Ravyn, Gateway, post

database = Database("postgresql+asyncpg://user:password@host:port/database")
registry = Registry(database=database)


class User(BaseModel):
    name: str
    email: str
    password: str
    retype_password: str


@post("/create", tags=["user"], description="Creates a new user in the database")
async def create_user(data: User) -> None:
    # Logic to create the user
    ...


app = Ravyn(
    routes=[Gateway(handler=create_user)],
    on_startup=[database.__aenter__],
    on_shutdown=[database.__aexit__],
)

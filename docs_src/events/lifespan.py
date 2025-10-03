from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: Ravyn):
    # What happens on startup
    async with registry:
        yield


app = Ravyn(
    routes=[Gateway(handler=create_user)],
    lifespan=lifespan,
)

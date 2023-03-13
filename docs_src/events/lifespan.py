from contextlib import asynccontextmanager

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, post
from saffier import Database, Registry

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
async def lifespan(app: Esmerald):
    # What happens on startup
    await database.connect()
    yield
    # What happens on shutdown
    await database.disconnect()


app = Esmerald(
    routes=[Gateway(handler=create_user)],
    lifespan=lifespan,
)

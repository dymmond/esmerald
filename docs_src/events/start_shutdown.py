from pydantic import BaseModel
from saffier import Database, Registry

from esmerald import Esmerald, Gateway, post

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


app = Esmerald(
    routes=[Gateway(handler=create_user)],
    on_startup=[database.connect],
    on_shutdown=[database.disconnect],
)

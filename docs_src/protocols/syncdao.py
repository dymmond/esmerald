from typing import Any, List

from esmerald import AsyncDAOProtocol, DaoProtocol, Esmerald, Gateway, post
from myapp.accounts.models import User
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, IntegrityError


class UserModel(BaseModel):
    name: str
    email: str


class UserDAO(DaoProtocol):
    model = User

    def get(self, obj_id: int) -> model:
        # logic to get the user
        ...

    def get_all(self, **kwargs: Any) -> List[User]:
        # logic to get all the users
        ...

    def update(self, obj_id: int) -> None:
        # logic to update the user
        ...

    def delete(self, obj_id: int) -> None:
        # logic to delete a user
        ...

    def create(self, user: UserModel) -> Any:
        # logic to create the user
        # send email
        # call external service
        # save in a different external database
        ...


class AsyncUserDAO(AsyncDAOProtocol):
    model = User

    async def get(self, obj_id: int) -> model:
        # logic to get the user
        try:
            await self.model.get(pk=obj_id)
        except DoesNotExist:
            ...

    async def get_all(self, **kwargs: Any) -> List[User]:
        # logic to get all the users
        ...

    async def update(self, obj_id: int) -> None:
        # logic to update the user
        ...

    async def delete(self, obj_id: int) -> None:
        # logic to delete a user
        ...

    async def create(self, user: UserModel) -> Any:
        # logic to create the user
        # send email
        # call external service
        # save in a different external database
        try:
            await self.model.create(**user)
        except IntegrityError:
            ...


@post("/create")
async def create(data: UserModel) -> None:
    user = UserDAO()
    user.create(user=data)


@post("/create-async-dao")
async def create_async_dao(data: UserModel) -> None:
    user = AsyncUserDAO()
    user.create(user=data)


app = Esmerald(
    routes=[
        Gateway(handler=create),
        Gateway(handler=create_async_dao),
    ]
)

from typing import TYPE_CHECKING, Any, List

from myapp.accounts.models import User
from pydantic import BaseModel
from saffier.exceptions import ObjectNotFound, SaffierException

from esmerald import AsyncDAOProtocol, DaoProtocol, Esmerald, Gateway, post

if TYPE_CHECKING:
    from esmerald.types import DictAny


class UserModel(BaseModel):
    name: str
    email: str


class UserDAO(DaoProtocol):
    model = User

    def get(self, obj_id: int, **kwargs: "DictAny") -> model:
        # logic to get the user
        ...

    def get_all(self, **kwargs: "DictAny") -> List[User]:
        # logic to get all the users
        ...

    def update(self, obj_id: int, user: UserModel, **kwargs: "DictAny") -> None:
        # logic to update the user
        ...

    def delete(self, obj_id: int, **kwargs: "DictAny") -> None:
        # logic to delete a user
        ...

    def create(self, user: UserModel, **kwargs: "DictAny") -> Any:
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
        except ObjectNotFound:
            ...

    async def get_all(self, **kwargs: "DictAny") -> List[User]:
        # logic to get all the users
        ...

    async def update(self, obj_id: int, user: UserModel, **kwargs: "DictAny") -> None:
        # logic to update the user
        ...

    async def delete(self, obj_id: int, **kwargs: "DictAny") -> None:
        # logic to delete a user
        ...

    async def create(self, user: UserModel, **kwargs: "DictAny") -> Any:
        # logic to create the user
        # send email
        # call external service
        # save in a different external database
        try:
            await self.model.create(**user)
        except SaffierException:
            ...


@post("/create")
async def create(data: UserModel) -> None:
    user = UserDAO()
    user.create(user=data)


@post("/create-async-dao")
async def create_async_dao(data: UserModel) -> None:
    user = AsyncUserDAO()
    await user.create(user=data)


app = Esmerald(
    routes=[
        Gateway(handler=create),
        Gateway(handler=create_async_dao),
    ]
)

from typing import Any, List, TypeVar

from typing_extensions import Protocol, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class AsyncDAOProtocol(Protocol):  # pragma: no cover
    """
    Async Data Access Object (AsyncDAO) is an abstract pattern widely used to
    separate the underlying logic of the database from the business logic.

    Esmerald definition of an AsyncDAO will contain the base patterns for an object.
    """

    model: Any

    """
    The model object. Usually this object is what allows the connection and
    data access to a database.
    """

    async def get(self, obj_id: Any, **kwargs: Any) -> Any: ...

    async def get_all(self, **kwargs: Any) -> List[Any]: ...

    async def update(self, obj_id: Any, **kwargs: Any) -> Any: ...

    async def delete(self, obj_id: Any, **kwargs: Any) -> Any: ...

    async def create(self, **kwargs: Any) -> Any: ...

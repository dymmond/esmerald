from typing import Any, List, TypeVar

from typing_extensions import Protocol, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class DaoProtocol(Protocol):  # pragma: no cover
    """
    Data Access Object (DAO) is an abstract pattern widely used to
    separate the underlying logic of the database from the business logic.

    Esmerald definition of a DAO will contain the base patterns for an object
    """

    @property
    def model(self) -> Any:
        ...

    """
    The model object. Usually this object is what allows the connection and
    data access to a database.
    """

    def get(self, obj_id: Any) -> Any:
        ...

    def get_all(self, **kwargs: Any) -> List[Any]:
        ...

    def update(self, obj_id: Any, **kwargs: Any) -> Any:
        ...

    def delete(self, obj_id: Any) -> Any:
        ...

    def create(self, **kwargs: Any) -> Any:
        ...

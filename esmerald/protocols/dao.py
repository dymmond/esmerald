from typing import TYPE_CHECKING, Any, List, TypeVar

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from esmerald.types import DictAny

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

    def get(self, obj_id: Any, **kwargs: "DictAny") -> Any:
        ...

    def get_all(self, **kwargs: "DictAny") -> List[Any]:
        ...

    def update(self, obj_id: Any, **kwargs: "DictAny") -> Any:
        ...

    def delete(self, obj_id: Any, **kwargs: "DictAny") -> Any:
        ...

    def create(self, **kwargs: "DictAny") -> Any:
        ...

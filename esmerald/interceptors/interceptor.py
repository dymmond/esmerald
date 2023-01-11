from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from starlette.types import Receive, Scope, Send


class EsmeraldInterceptor(ABC):
    """Base class for any Esmerald interceptor in the system."""

    @abstractmethod
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        The abstract method that needs to be implemented for any interceptor.
        """
        raise NotImplementedError("intercept must be implemented")

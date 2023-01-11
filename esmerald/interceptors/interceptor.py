from abc import ABC
from typing import TYPE_CHECKING

from esmerald.protocols.interceptor import InterceptorProtocol

if TYPE_CHECKING:
    from starlette.types import Receive, Scope, Send


class EsmeraldInterceptor(ABC, InterceptorProtocol):
    """Base class for any Esmerald interceptor in the system."""

    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        The abstract method that needs to be implemented for any interceptor.
        """
        raise NotImplementedError("intercept must be implemented")

from typing import TYPE_CHECKING, TypeVar

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from starlette.types import Receive, Scope, Send

T = TypeVar("T")


@runtime_checkable
class InterceptorProtocol(Protocol):  # pragma: no cover
    """
    Generic object serving the base for interception of messages,
    before reaching the endpoint. This is inspired by the AOP (Aspect Oriented Programming).

    The interceptor is handled between the call and the API endpoint itself and acts on it.

    An interceptor could be anything from logging to rerouting or even input sanitizing.
    """

    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        ...

from lilya import status
from lilya.protocols.permissions import PermissionProtocol
from lilya.types import Receive, Scope, Send

from esmerald import Include
from esmerald.exceptions import NotAuthorized, PermissionDenied
from esmerald.permissions import BasePermission
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.testclient import create_client


class EsmeraldPermission(BasePermission):
    def has_permission(self, request, apiview):
        if not request.headers.get("allow_all"):
            return False
        return True


# Testing for lilya permissions
class LilyaDeny(PermissionProtocol):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotAuthorized()


class LilyaPermDeny(PermissionProtocol):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)
        if request.headers.get("allow_all"):
            await self.app(scope, receive, send)
            return
        raise PermissionDenied()


def test_mix_permissions_with_native_esmerald() -> None:
    @get(path="/secret", permissions=[LilyaDeny])
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler, permissions=[EsmeraldPermission])],
    ) as client:
        response = client.get("/secret")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.json().get("detail")
            == "Not Authorized."
        )
        response = client.get("/secret", headers={"Authorization": "yes"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.json().get("detail")
            == "Not Authorized."
        )
        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_two_permissions_mixed_same_level() -> None:
    @get(path="/secret", permissions=[EsmeraldPermission, LilyaDeny])
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[Gateway(handler=my_http_route_handler)],
    ) as client:
        response = client.get("/secret")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.get("/secret", headers={"Authorization": "yes"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert (
            response.json().get("detail")
            == "Not Authorized."
        )
        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_include() -> None:
    @get(path="/secret")
    def my_http_route_handler() -> None: ...

    with create_client(
        routes=[
            Include(routes=[Gateway(handler=my_http_route_handler)], permissions=[LilyaDeny]),
        ],
        permissions=[EsmeraldPermission],
    ) as client:
        response = client.get("/secret", headers={"Authorization": "yes", "allow_all": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

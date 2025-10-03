import pytest

from ravyn import (
    APIView,
    Gateway,
    ImproperlyConfigured,
    WebhookGateway,
    whdelete,
    whget,
    whhead,
    whoptions,
    whpatch,
    whpost,
    whput,
    whroute,
    whtrace,
)
from ravyn.testclient import create_client


@whpost("new-event")
async def new_event() -> None:
    """"""


@whpost("/event")
async def event() -> None:
    """"""


class MyView(APIView):
    @whpost("new-event")
    async def new_event(self) -> None:
        """"""

    @whpost("/event")
    async def event(self) -> None:
        """"""


def test_raise_improperly_configured_for_ravyn_routes(test_client_factory):
    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[WebhookGateway(handler=new_event)]):
            """"""


def test_raise_improperly_configured_for_webhooks(test_client_factory):
    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[], webhooks=[Gateway(handler=event)]):
            """"""


def test_can_generate_webhooks_from_apiview(test_client_factory):
    with create_client(routes=[], webhooks=[WebhookGateway(handler=MyView)]) as client:
        assert len(client.app.webhooks) == 2


@pytest.mark.parametrize(
    "verb,is_route",
    [
        (whpost, False),
        (whdelete, False),
        (whhead, False),
        (whget, False),
        (whoptions, False),
        (whpatch, False),
        (whput, False),
        (whtrace, False),
        (whroute, True),
    ],
)
def test_verbs(verb, is_route):
    if is_route:

        @verb("event", methods=["PUT", "POST", "DELETE", "GET"])
        async def event() -> None:
            """"""

    else:

        @verb("event")
        async def event() -> None:
            """"""

    with create_client(routes=[], webhooks=[WebhookGateway(handler=event)]) as client:
        assert len(client.app.webhooks) == 1

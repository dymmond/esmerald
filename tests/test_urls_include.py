import pytest

from esmerald import Gateway, ImproperlyConfigured, get
from esmerald.core.urls.base import include


@get("/home")
async def home() -> None:
    """"""


route_patterns = [Gateway(handler=home)]


def test_default_include_router_patterns():
    include_routes = include("tests.test_urls_include")

    assert len(include_routes) == 1


my_urls = [Gateway(handler=home)]


def test_pattern_include():
    include_routes = include("tests.test_urls_include", pattern="my_urls")

    assert len(include_routes) == 1


def test_raises_improperly_configured():
    with pytest.raises(ImproperlyConfigured):
        include(1, pattern="my_urls")

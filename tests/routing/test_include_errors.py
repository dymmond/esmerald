import pytest

from esmerald import Gateway, ImproperlyConfigured, Include, get


@get()
async def home() -> None:
    """"""


gateway = Gateway(handler=home)


route_patterns = [Gateway(handler=home)]


def test_raise_error_namespace_and_routes():
    with pytest.raises(ImproperlyConfigured):
        Include(namespace="test", routes=[gateway])


@pytest.mark.parametrize("arg", [gateway, 2, get])
def test_raise_error_namespace(arg):
    with pytest.raises(ImproperlyConfigured):
        Include(namespace=arg)


@pytest.mark.parametrize("arg", [gateway, 2, get])
def test_raise_error_pattern(arg):
    with pytest.raises(ImproperlyConfigured):
        Include(pattern=arg, routes=[gateway])


def test_raise_error_pattern_and_routes():
    with pytest.raises(ImproperlyConfigured):
        Include(pattern="test", routes=[gateway])


def test_namespace_include_routes():
    include = Include(namespace="tests.routing.test_include_errors")

    assert len(include.routes) == 1

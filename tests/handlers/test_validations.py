import pytest

from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.router import HTTPHandler


def test_raise_no_function_validation() -> None:
    handler = HTTPHandler(path="/")

    with pytest.raises(ImproperlyConfigured):
        handler.check_handler_function()

    with pytest.raises(RuntimeError):
        handler.get_dependencies()

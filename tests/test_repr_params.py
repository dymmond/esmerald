import pytest

from ravyn import Body, Cookie, File, Form, Param, Path, Query


def test_reprs_body():
    body = Body(annotation=str, default=None)

    assert repr(body) == "Body(annotation=<class 'str'>, default=None)"


@pytest.mark.parametrize("obj", [Body, Cookie, Form, Param, Path, Query, File])
def test_reprs_param(obj):
    param = obj(annotation=str, default=None)

    assert repr(param) == f"{obj.__name__}(annotation=<class 'str'>, default=None)"

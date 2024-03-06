import json
from typing import Any

from lilya.exceptions import HTTPException as StarletteHTTPException
from lilya.status import HTTP_500_INTERNAL_SERVER_ERROR

from esmerald.exceptions import HTTPException
from esmerald.middleware.exceptions import EsmeraldAPIExceptionMiddleware
from esmerald.requests import Request


async def dummy_app(scope: Any, receive: Any, send: Any) -> None:
    """ """


middleware = EsmeraldAPIExceptionMiddleware(dummy_app, False, {})


def test_default_handle_http_exception_handling_extra_object() -> None:
    response = middleware.default_http_exception_handler(
        Request(scope={"type": "http", "method": "GET"}),  # type: ignore
        HTTPException(detail="esmerald exception", extra={"test": "fluid"}),
    )

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body) == {
        "detail": "esmerald exception",
        "extra": {"test": "fluid"},
        "status_code": 500,
    }


def test_default_handle_http_exception_handling_extra_none() -> None:
    response = middleware.default_http_exception_handler(
        Request(scope={"type": "http", "method": "GET"}),  # type: ignore
        HTTPException(detail="esmerald exception"),
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body) == {
        "detail": "esmerald exception",
        "status_code": 500,
    }


def test_default_handle_esmerald_http_exception_handling() -> None:
    response = middleware.default_http_exception_handler(
        Request(scope={"type": "http", "method": "GET"}),  # type: ignore
        HTTPException(detail="esmerald exception"),
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body) == {
        "detail": "esmerald exception",
        "status_code": 500,
    }


def test_default_handle_esmerald_http_exception_extra_list() -> None:
    response = middleware.default_http_exception_handler(
        Request(scope={"type": "http", "method": "GET"}),  # type: ignore
        HTTPException(detail="esmerald exception", extra=["extra-1", "extra-2"]),
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body) == {
        "detail": "esmerald exception",
        "extra": ["extra-1", "extra-2"],
        "status_code": 500,
    }


def test_default_handle_starlette_http_exception_handling() -> None:
    response = middleware.default_http_exception_handler(
        Request(scope={"type": "http", "method": "GET"}),  # type: ignore
        StarletteHTTPException(
            detail="esmerald exception", status_code=HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body) == {
        "detail": "esmerald exception",
        "status_code": 500,
    }


def test_default_handle_python_http_exception_handling() -> None:
    response = middleware.default_http_exception_handler(
        Request(scope={"type": "http", "method": "GET"}), AttributeError("oops")  # type: ignore
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body) == {
        "detail": repr(AttributeError("oops")),
        "status_code": HTTP_500_INTERNAL_SERVER_ERROR,
    }
